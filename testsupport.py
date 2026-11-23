"""Controlled-output local SDK substitute; not GenVM or real-model evidence."""
import copy
from datetime import datetime, timezone
import importlib.util
import pathlib
import sys
import types


class UserError(Exception):
    pass


class Return:
    def __init__(self, calldata):
        self.calldata = calldata


def exact(*clauses):
    return {"clauses": [{"clause_id": i, "status": "EXACT", "constraints": bounds}
                        for i, bounds in enumerate(clauses)], "whole_translation": "EXACT"}


def bound(source, destination, maximum):
    return {"from_id": source, "to_id": destination, "max_seconds": maximum}


class Runtime:
    def __init__(self):
        self.sender = "0x" + "1" * 40
        self.clock = 1_800_000_000
        self.output = exact([bound(2, 1, -60)])
        self.validator_output = None
        self.mutate = None
        self.prompts = []
        self.calls = 0
        self.clock_reads = 0
        self.in_nondet = False
        self.phase = "leader"
        self.fake = None

    def as_sender(self, address):
        self.sender = address
        self.fake.message.sender_address = address

    def prompt(self, prompt, response_format=None):
        assert response_format == "json"
        self.prompts.append({"phase": self.phase, "prompt": prompt})
        self.calls += 1
        value = self.validator_output if self.phase == "validator" and self.validator_output is not None else self.output
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value)

    def run(self, leader, validator):
        self.in_nondet = True
        try:
            self.phase = "leader"
            candidate = leader()
            if self.mutate:
                candidate = self.mutate(copy.deepcopy(candidate))
            self.phase = "validator"
            if not validator(Return(candidate)):
                raise AssertionError("Independent validator rejected complete receipt")
            return candidate
        finally:
            self.in_nondet = False
            self.phase = "leader"


def load():
    runtime = Runtime()
    fake = types.ModuleType("genlayer")
    fake.contract = types.SimpleNamespace(Contract=object)
    fake.storage = types.SimpleNamespace(TreeMap=dict)
    fake.public = types.SimpleNamespace(write=lambda f: f, view=lambda f: f)
    fake.message = types.SimpleNamespace(sender_address=runtime.sender)
    fake.nondet = types.SimpleNamespace(exec_prompt=runtime.prompt)
    fake.vm = types.SimpleNamespace(UserError=UserError, Return=Return, run_nondet_default=runtime.run)
    type_module = types.ModuleType("genlayer.types")
    type_module.u64 = int
    type_module.__all__ = ["u64"]
    previous = {name: sys.modules.get(name) for name in ["genlayer", "genlayer.types"]}
    sys.modules["genlayer"] = fake
    sys.modules["genlayer.types"] = type_module
    spec = importlib.util.spec_from_file_location("OrderWindow", pathlib.Path(__file__).with_name("OrderWindow.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        for name, old in previous.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old

    class TransactionDateTime:
        @staticmethod
        def now(tz=None):
            if runtime.in_nondet:
                raise AssertionError("Clock must be captured outside nondeterministic callbacks")
            assert tz is timezone.utc
            runtime.clock_reads += 1
            return datetime.fromtimestamp(runtime.clock, tz)

    module.datetime = TransactionDateTime
    runtime.fake = fake
    contract = module.OrderWindow()
    for name, annotation in module.OrderWindow.__annotations__.items():
        if getattr(annotation, "__origin__", None) is dict:
            setattr(contract, name, {})
    return module, contract, runtime

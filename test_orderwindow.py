"""Deterministic state/solver and adversarial receipt tests with controlled model output."""
import copy
import json
import unittest
from testsupport import load, bound, exact, UserError

OWNER = "0x" + "1" * 40
OTHER = "0x" + "2" * 40


class OrderWindowTests(unittest.TestCase):
    def setUp(self):
        self.m, self.c, self.r = load()
        self.events = [{"name": "Build", "description": "Actor declares build recorded.", "actor": OWNER},
                       {"name": "Publish", "description": "Actor declares publication recorded.", "actor": OTHER}]
        self.clauses = ["Publish is at least 60 seconds after Build."]

    def open(self, horizon=120, activation=600):
        return self.c.open_plan("Release sequence", "Order authenticated technical declarations.",
                                json.dumps(self.events), json.dumps(self.clauses), horizon, activation)

    def compiled(self, horizon=120):
        plan_id = self.open(horizon)
        self.c.compile_plan(plan_id)
        return plan_id

    def active(self, horizon=120):
        plan_id = self.compiled(horizon)
        self.c.activate_plan(plan_id, self.c.get_plan(plan_id)["receipt_hash"])
        return plan_id

    def snapshot(self):
        return copy.deepcopy((self.c.plans, self.c.attempts, self.c.plan_count, self.c.event_marks))

    def test_full_input_hash_and_canonical_receipt(self):
        pid = self.compiled()
        p = self.c.get_plan(pid)
        self.assertEqual(p["receipt"]["plan"], p["core"])
        self.assertEqual(p["receipt_hash"], self.m._hash(self.m._json(p["receipt"])))
        self.assertTrue(p["receipt"]["inspection"]["semantic_complete"])
        self.assertEqual(len(self.r.prompts), 2)
        self.assertEqual(self.r.prompts[0]["prompt"], self.r.prompts[1]["prompt"])

    def test_negative_minimum_bound_produces_tight_windows(self):
        pid = self.compiled()
        windows = self.c.get_plan(pid)["receipt"]["event_windows"]
        self.assertEqual(windows, [{"event_id": 1, "earliest_offset": 0, "latest_offset": 60},
                                  {"event_id": 2, "earliest_offset": 60, "latest_offset": 120}])

    def test_negative_cycle_fails_without_activation(self):
        self.r.output = exact([bound(2, 1, -60), bound(1, 2, -1)])
        pid = self.compiled()
        self.assertEqual(self.c.get_plan(pid)["status"], "INFEASIBLE")
        self.assertFalse(self.c.get_plan(pid)["receipt"]["activation_allowed"])
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, self.c.get_plan(pid)["receipt_hash"])

    def test_tightest_pair_normalized_independent_of_order(self):
        core = self.c.get_plan(self.open())["core"]
        a = self.m._normalize(exact([bound(2, 1, -10), bound(2, 1, -60), bound(0, 1, 120)]), core)
        b = self.m._normalize(exact([bound(0, 1, 120), bound(2, 1, -60)]), core)
        self.assertEqual(a, b)

    def test_activation_relative_origin_and_immutable_deadline(self):
        pid = self.compiled()
        initial = self.c.get_plan(pid)
        self.r.clock += 100
        self.c.activate_plan(pid, initial["receipt_hash"])
        p = self.c.get_plan(pid)
        self.assertEqual(p["origin_at"], self.r.clock)
        self.assertEqual(p["horizon_at"], self.r.clock + 120)
        self.assertEqual(p["core"]["activation_until"], initial["core"]["activation_until"])
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, p["receipt_hash"])

    def test_exact_hash_and_owner_required_for_activation(self):
        pid = self.compiled()
        before = self.snapshot()
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, "0" * 64)
        self.r.as_sender(OTHER)
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, self.c.get_plan(pid)["receipt_hash"])
        self.assertEqual(before, self.snapshot())

    def test_build_late_rejected_despite_own_horizon(self):
        pid = self.active()
        self.r.clock += 90
        before = self.snapshot()
        self.assertFalse(self.c.preview_event(pid, 1)["admissible"])
        with self.assertRaises(UserError):
            self.c.record_event(pid, 1)
        self.assertEqual(before, self.snapshot())

    def test_global_unrecorded_floor_not_only_hypothetical_event(self):
        self.r.output = exact([bound(1, 0, -60), bound(0, 1, 60)])
        pid = self.active()
        self.r.clock += 61
        self.r.as_sender(OTHER)
        self.assertFalse(self.c.preview_event(pid, 2)["admissible"])
        with self.assertRaises(UserError):
            self.c.record_event(pid, 2)

    def test_fixed_prior_marks_and_minimum_separation(self):
        pid = self.active()
        self.c.record_event(pid, 1)
        self.r.as_sender(OTHER)
        self.r.clock += 59
        with self.assertRaises(UserError):
            self.c.record_event(pid, 2)
        self.r.clock += 1
        self.c.record_event(pid, 2)
        self.assertEqual(self.c.get_plan(pid)["status"], "COMPLETED")

    def test_maximum_separation_cannot_be_evaded(self):
        self.r.output = exact([bound(1, 2, 10)])
        pid = self.active()
        self.c.record_event(pid, 1)
        self.r.clock += 11
        self.r.as_sender(OTHER)
        with self.assertRaises(UserError):
            self.c.record_event(pid, 2)
        self.assertEqual(self.c.get_feasibility(pid)["effective_status"], "UNSCHEDULABLE")

    def test_same_timestamp_declarations_supported_when_inclusive(self):
        self.r.output = exact([bound(1, 2, 0), bound(2, 1, 0)])
        pid = self.active()
        self.c.record_event(pid, 1)
        self.r.as_sender(OTHER)
        self.c.record_event(pid, 2)
        marks = self.c.get_plan(pid)["marks"]
        self.assertEqual(marks["1"]["offset_seconds"], marks["2"]["offset_seconds"])

    def test_horizon_boundary_inclusive_and_completion_terminal(self):
        pid = self.active()
        self.r.clock += 60
        self.c.record_event(pid, 1)
        self.r.clock += 60
        self.r.as_sender(OTHER)
        self.c.record_event(pid, 2)
        self.r.clock += 1000
        self.assertEqual(self.c.get_feasibility(pid)["effective_status"], "COMPLETED")
        self.r.as_sender(OWNER)
        with self.assertRaises(UserError):
            self.c.retire_plan(pid)
        with self.assertRaises(UserError):
            self.c.expire_plan(pid)

    def test_actor_authentication_and_replay(self):
        pid = self.active()
        before = self.snapshot()
        with self.assertRaises(UserError):
            self.c.record_event(pid, 2)
        self.assertEqual(before, self.snapshot())
        self.c.record_event(pid, 1)
        before = self.snapshot()
        with self.assertRaises(UserError):
            self.c.record_event(pid, 1)
        self.assertEqual(before, self.snapshot())

    def test_reverse_clock_rejects_without_storage_change(self):
        pid = self.active()
        self.r.clock += 10
        self.c.record_event(pid, 1)
        before = self.snapshot()
        self.r.clock -= 1
        with self.assertRaises(UserError):
            self.c.get_feasibility(pid)
        with self.assertRaises(UserError):
            self.c.retire_plan(pid)
        self.assertEqual(before, self.snapshot())

    def test_rejected_mark_does_not_advance_clock_floor(self):
        pid = self.active()
        origin = self.r.clock
        self.r.clock += 90
        with self.assertRaises(UserError):
            self.c.record_event(pid, 1)
        self.r.clock = origin + 30
        self.c.record_event(pid, 1)
        self.assertEqual(self.c.get_plan(pid)["marks"]["1"]["offset_seconds"], 30)

    def test_views_do_not_write_or_advance_floor(self):
        pid = self.active()
        self.r.clock += 50
        before = self.snapshot()
        self.c.get_feasibility(pid)
        self.c.preview_event(pid, 1)
        self.c.get_plan(pid)
        self.assertEqual(before, self.snapshot())

    def test_activation_expiry_at_boundary_permissionless(self):
        pid = self.compiled()
        self.r.clock += 600
        before = self.snapshot()
        self.assertEqual(self.c.get_feasibility(pid)["effective_status"], "EXPIRED")
        self.assertEqual(before, self.snapshot())
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, self.c.get_plan(pid)["receipt_hash"])
        self.r.as_sender(OTHER)
        self.c.expire_plan(pid)
        self.assertEqual(self.c.get_plan(pid)["expiry_reason"], "ACTIVATION_WINDOW_ELAPSED")

    def test_expired_active_plan_cannot_be_rescued(self):
        pid = self.active()
        self.r.clock += 121
        self.assertEqual(self.c.get_feasibility(pid)["effective_status"], "UNSCHEDULABLE")
        with self.assertRaises(UserError):
            self.c.record_event(pid, 1)
        self.r.as_sender(OTHER)
        self.c.expire_plan(pid)
        self.assertEqual(self.c.get_plan(pid)["status"], "EXPIRED")
        self.r.as_sender(OWNER)
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, self.c.get_plan(pid)["receipt_hash"])

    def test_expire_while_feasible_rejects(self):
        pid = self.active()
        before = self.snapshot()
        with self.assertRaises(UserError):
            self.c.expire_plan(pid)
        self.assertEqual(before, self.snapshot())

    def test_retirement_irreversible_and_owner_only(self):
        pid = self.compiled()
        self.r.as_sender(OTHER)
        with self.assertRaises(UserError):
            self.c.retire_plan(pid)
        self.r.as_sender(OWNER)
        self.c.retire_plan(pid)
        self.assertEqual(self.c.get_plan(pid)["status"], "RETIRED")
        for action in [lambda: self.c.compile_plan(pid), lambda: self.c.activate_plan(pid, self.c.get_plan(pid)["receipt_hash"])]:
            with self.assertRaises(UserError):
                action()

    def test_unsupported_clause_blocks_entire_plan(self):
        self.clauses.append("Publish before Build, unless skipped.")
        self.r.output["clauses"].append({"clause_id": 1, "status": "UNSUPPORTED", "constraints": []})
        pid = self.compiled()
        receipt = self.c.get_plan(pid)["receipt"]
        self.assertEqual(receipt["decision"], "UNSUPPORTED")
        self.assertEqual(receipt["compiled_constraints"], [])
        with self.assertRaises(UserError):
            self.c.compile_plan(pid)

    def test_uncertain_whole_translation_blocks_exact_rows(self):
        self.r.output["whole_translation"] = "UNCERTAIN"
        pid = self.compiled()
        self.assertEqual(self.c.get_plan(pid)["status"], "INCONCLUSIVE")
        self.assertFalse(self.c.get_feasibility(pid)["can_activate"])

    def test_prompt_explicitly_forbids_approximating_unsupported_language(self):
        pid = self.compiled()
        prompt = self.r.prompts[0]["prompt"]
        for term in ["Strict comparisons", "fractional", "conditional", "logically equivalent", "not just sufficient"]:
            self.assertIn(term, prompt)
        self.assertEqual(self.c.get_plan(pid)["status"], "COMPILED")

    def test_malformed_output_three_attempt_limit_and_history(self):
        self.r.output = {"clauses": []}
        pid = self.open()
        for attempt in range(1, 4):
            self.c.compile_plan(pid)
            self.assertEqual(self.c.get_attempt(pid, attempt)["attempt"], attempt)
        self.assertEqual(self.c.get_plan(pid)["status"], "UNRESOLVED_FINAL")
        before = self.snapshot()
        with self.assertRaises(UserError):
            self.c.compile_plan(pid)
        self.assertEqual(before, self.snapshot())

    def test_technical_exception_retry_then_exact(self):
        pid = self.open()
        self.r.output = RuntimeError("model unavailable")
        self.c.compile_plan(pid)
        self.assertEqual(self.c.get_plan(pid)["status"], "RETRYABLE")
        self.r.output = exact([bound(2, 1, -60)])
        self.c.compile_plan(pid)
        self.assertEqual(self.c.get_plan(pid)["status"], "COMPILED")
        self.assertEqual(self.c.get_attempt(pid, 1)["decision"], "UNRESOLVED")

    def test_boolean_ids_and_bounds_rejected(self):
        for field in ["clause_id", "from_id", "to_id", "max_seconds"]:
            with self.subTest(field=field):
                self.setUp()
                if field == "clause_id":
                    self.r.output["clauses"][0][field] = False
                else:
                    self.r.output["clauses"][0]["constraints"][0][field] = True
                pid = self.compiled()
                self.assertEqual(self.c.get_plan(pid)["status"], "RETRYABLE")
        with self.assertRaises(UserError):
            self.c.get_plan(False)

    def test_missing_extra_and_duplicate_clause_ids_fail_schema(self):
        for mutate in [lambda x: x.update({"extra": 1}),
                       lambda x: x["clauses"][0].update({"clause_id": 1}),
                       lambda x: x["clauses"][0].update({"constraints": []}),
                       lambda x: x["clauses"][0]["constraints"][0].update({"extra": 1})]:
            with self.subTest(mutate=mutate):
                self.setUp()
                mutate(self.r.output)
                self.assertEqual(self.c.get_plan(self.compiled())["status"], "RETRYABLE")

    def test_unsupported_partial_constraints_fail_schema(self):
        self.r.output["clauses"][0]["status"] = "UNSUPPORTED"
        pid = self.compiled()
        self.assertEqual(self.c.get_plan(pid)["status"], "RETRYABLE")

    def test_independent_semantic_disagreement_leaves_no_state(self):
        pid = self.open()
        self.r.validator_output = exact([bound(2, 1, -59)])
        before = self.snapshot()
        with self.assertRaises(AssertionError):
            self.c.compile_plan(pid)
        self.assertEqual(before, self.snapshot())

    def test_every_receipt_leaf_tampering_rejected(self):
        pid = self.compiled()
        receipt = self.c.get_plan(pid)["receipt"]

        def paths(value, prefix=()):
            if isinstance(value, dict):
                for k, v in value.items():
                    yield from paths(v, prefix + (k,))
            elif isinstance(value, list) and value:
                for k, v in enumerate(value):
                    yield from paths(v, prefix + (k,))
            else:
                yield prefix

        all_paths = list(paths(receipt))
        self.assertGreater(len(all_paths), 60)
        for path in all_paths:
            self.setUp()
            pid = self.open()
            def mutate(candidate, target=path):
                cursor = candidate
                for key in target[:-1]:
                    cursor = cursor[key]
                old = cursor[target[-1]]
                cursor[target[-1]] = (not old if isinstance(old, bool) else old + 1 if type(old) is int
                                     else old + "!" if isinstance(old, str) else ["changed"] if old == [] else "changed")
                return candidate
            self.r.mutate = mutate
            before = self.snapshot()
            with self.subTest(path=path), self.assertRaises(AssertionError):
                self.c.compile_plan(pid)
            self.assertEqual(before, self.snapshot())

    def test_graph_hash_alone_cannot_authorize_modified_graph(self):
        pid = self.compiled()
        p = self.c.get_plan(pid)
        p["receipt"]["compiled_constraints"][0]["max_seconds"] += 1
        p["receipt_hash"] = self.m._hash(self.m._json(p["receipt"]))
        self.c.plans[str(pid)] = self.m._json(p)
        with self.assertRaises(UserError):
            self.c.activate_plan(pid, p["receipt_hash"])

    def test_maximum_unicode_inputs_fully_inspected(self):
        # JSON transport uses escaped surrogate pairs; prompt keeps complete Unicode.
        self.events = [{"name": str(i) + "😀" * 79, "description": "😀" * 400, "actor": OWNER} for i in range(5)]
        self.clauses = [str(i) + "😀" * 599 for i in range(5)]
        self.r.output = exact(*[[bound(0, 0, 0)] for _ in range(5)])
        pid = self.c.open_plan("😀" * 120, "😀" * 600, json.dumps(self.events), json.dumps(self.clauses), 86400, 86400)
        receipt = self.c.compile_plan(pid)
        inspection = receipt["inspection"]
        prompt = self.r.prompts[0]["prompt"]
        self.assertEqual(inspection["prompt_chars"], len(prompt))
        self.assertEqual(inspection["prompt_utf8_bytes"], len(prompt.encode("utf-8")))
        self.assertFalse(inspection["prompt_truncated"])
        self.assertIn(self.clauses[-1], prompt)

    def test_budget_never_slices_and_rejects_before_write(self):
        self.m.MAX_PROMPT_BYTES = 10
        before = self.snapshot()
        with self.assertRaises(UserError):
            self.open()
        self.assertEqual(before, self.snapshot())

    def test_input_limits_types_duplicate_and_surrogate_reject(self):
        for change in [lambda: self.events.append(copy.deepcopy(self.events[0])),
                       lambda: self.events[0].update({"actor": "0x" + "0" * 40}),
                       lambda: self.events[0].update({"name": "\ud800"}),
                       lambda: self.clauses.append(self.clauses[0])]:
            self.setUp()
            change()
            with self.assertRaises(UserError):
                self.open()
            self.assertEqual(self.c.plan_count, 0)
        for h, a in [(True, 600), (59, 600), (86401, 600), (120, False)]:
            self.setUp()
            with self.assertRaises(UserError):
                self.open(h, a)

    def test_clock_captured_once_outside_callbacks(self):
        pid = self.open()
        reads = self.r.clock_reads
        receipt = self.c.compile_plan(pid)
        self.assertEqual(self.r.clock_reads - reads, 1)
        self.assertEqual(receipt["assessed_at"], self.r.clock)

    def test_multi_plan_isolation(self):
        first = self.active()
        second = self.compiled()
        before = self.c.get_plan(first)
        self.c.retire_plan(second)
        self.assertEqual(self.c.get_plan(first), before)
        self.assertEqual(self.c.get_stats()["plans"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

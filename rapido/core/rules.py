from .database import ANNOTATION_KEY as KEY


class RuleAssignee:

    @property
    def assigned_rules(self):
        return self.annotations[KEY]['rules']

    def assign_rules(self, rules):
        self.annotations[KEY]['rules'] = rules
        db = self.database
        for rule_id in rules:
            rule = db.rules.get(rule_id)
            if not rule:
                continue
            self.annotations[KEY][rule_id + '_code'] = rule['code']
            self.annotations[KEY]['compiled_' + rule_id + '_code'] = None

    def filter_rules(self, rule_type):
        db_rules = self.database.rules
        filtered_rules = [rule for rule in self.assigned_rules
            if db_rules.has_key(rule) and db_rules[rule]['type'] == rule_type]
        return filtered_rules

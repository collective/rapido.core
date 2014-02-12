from .database import ANNOTATION_KEY as KEY


class RuleAssignee:

    @property
    def assigned_rules(self):
        return self.annotations[KEY]['rules']

    def assign_rules(self, rules):
        self.annotations[KEY]['rules'] = rules
        db = self.database
        for rule_id in rules:
            self.refresh_rule(rule_id)

    def refresh_rule(self, rule_id):
        annotation = self.annotations[KEY]
        if rule_id not in annotation['rules']:
            if annotation.has_key(rule_id + '_code'):
                del annotation[rule_id + '_code']
            if annotation.has_key('compiled_' + rule_id + '_code'):
                del annotation['compiled_' + rule_id + '_code']
        else:
            db = self.database
            rule = db.rules.get(rule_id)
            if not rule:
                return
            annotation[rule_id + '_code'] = rule['code']
            annotation['compiled_' + rule_id + '_code'] = None

    def filter_rules(self, rule_type):
        db_rules = self.database.rules
        filtered_rules = [rule for rule in self.assigned_rules
            if db_rules.has_key(rule) and db_rules[rule]['type'] == rule_type]
        return filtered_rules

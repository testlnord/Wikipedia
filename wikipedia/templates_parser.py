import collections

import re


class TemplateParser:
    def __init__(self, text):
        self._text = text.strip()

    Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

    def tokenize(self, text):
        token_specification = [
            ('OPENB', r'\{\{'),
            ('CLOSEB', r'\}\}'),
            ('TEXT', r'(([^\}\{])|(\{[^\{])|(\}[^\}]))+'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        get_token = re.compile(tok_regex, flags=re.S).match
        line = 1
        pos = line_start = 0
        mo = get_token(text)
        while mo is not None:
            typ = mo.lastgroup
            val = mo.group(typ)
            yield self.Token(typ, val, line, mo.start() - line_start)
            pos = mo.end()
            mo = get_token(text, pos)
        if pos != len(text):
            raise RuntimeError('Unexpected character %r on line %d in text %r' % (text[pos], line, text))

    def get_templates(self):
        """
        iterates over boxes in text
        :return: box in format "{{...}}"

        >>> statements = '''
        >>>{{box1}}{not box}}
        >>>not box either{{
        >>>box2{{inner box}}
        >>>}} text after'''

        >>>d = TemplateParser(statements)
        >>>for k in d.get_templates():
        >>>print(k)
        {{box1}}
        {{
        box2{{inner box}}
        }}
        """
        brackets_level = 0
        is_inside_brackets = False
        box_text = ''
        for token in self.tokenize(self._text):
            if token.typ == 'OPENB':
                brackets_level += 1
                is_inside_brackets = True
                box_text += '{{'
            elif token.typ == 'CLOSEB':
                if is_inside_brackets:
                    brackets_level -= 1
                    box_text += '}}'
                    if brackets_level == 0:
                        is_inside_brackets = False
                        yield box_text
                        box_text = ''
            else: # token.typ == 'TEXT'
                if is_inside_brackets:
                    if brackets_level == 1:
                        box_text += token.value
                    else:
                        box_text += token.value.replace("\n","\\n")
                else:
                    if token.value.strip():
                        break


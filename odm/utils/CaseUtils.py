def snake_to_camel(s: str) -> str:
    if s == '' or s is None:
        return ''
    if s[0] == '_':
        return s
    words = s.split('_')
    return words[0] + ''.join(word.title() for word in words[1:])


def camel_to_snake(s: str) -> str:
    res = []
    for char in s:
        if char.isalpha() and char.upper() == char:
            res.append('_')
            res.append(char.lower())
        else:
            res.append(char)

    return ''.join(res)

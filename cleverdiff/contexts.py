class DefaultContext:
    DESCRIPTION = "unformatted text file"

    def __init__(self, filename):
        self.label = filename

    def __getitem__(self, item):
        return f"{self.label}:{item}"


class EcflowContext:
    DESCRIPTION = "ecFlow suite definition"

    def __init__(self, filename):
        self.label = filename
        with open(filename, "rt") as f:
            self._context = self._create_context(f.read().splitlines())

    @classmethod
    def _create_context(cls, content):
        """
        Given string content, establish a human-readable context for each
        line.

        Arguments
        ---------
        content : list of str
            The contents to parse, as a list of strings (one string per line).

        Returns
        -------
        list
            A list of strings describing each line of the content.
        """
        result = []
        stack = [""]
        last_kw = None
        for line in content:
            line = line.strip()
            try:
                keyword, value = line.split()
            except ValueError:
                keyword = line
                value = ''
            if keyword in ['endsuite', 'endfamily']:
                stack.pop()
            if keyword in ['suite', 'family', 'task']:
                if last_kw == 'task':
                    stack.pop()
                last_kw = keyword
                stack.append(value)

            result.append('/'.join(stack))

        return result

    def __getitem__(self, item):
        return f"{self.label}:{self._context[item]}"


EXTENSION_MAPPING = {
    ".def": EcflowContext,
}


def lookup_extension(extension):
    return EXTENSION_MAPPING.get(extension, DefaultContext)

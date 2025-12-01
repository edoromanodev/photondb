"""
ASCII command parser (telnet-friendly)
"""


class AsciiParser:

    @staticmethod
    def parse_ascii_command(data: str) -> list:
        """
        Parse an ASCII command string into an argument list.
        ex1: "GET key" → ["GET", "key"]
        ex2: "SET name Alice" → ["SET", "name", "Alice"]


        Args:
            data (str): The received ASCII command string.

        Returns:
            list[str]: command and arguments as a list of strings.

        """

        data = data.strip()


        parts = data.split()

        return [part for part in parts if part]


class Encoder:
    """converts the results of telnet-formatted strings"""

        
    @staticmethod
    def format_response(result) -> str:

        """Format the result for telnet"""
        
        if result is None:
            return "(nil)"
        
        elif isinstance(result, bool):
            return "OK" if result else "FAIL"
        
        elif isinstance(result, int):
            return str(result)
        
        elif isinstance(result, str):
            return result
        
        elif isinstance(result, list):
            return '\n'.join(str(item) for item in result)
        
        elif isinstance(result, dict):
            lines = []
            for k, v in result.items():
                lines.append(f'"{k}" -> "{v}"')
            return '\n'.join(lines)
        
        else:
            return str(result)
class Flags:
    """
    Flags are used to configure the behavior of the queue and worker.

    Parameters
    ----------
    auto_convert_json_keys : bool
        If True, the queue will automatically convert JSON keys to strings. Useful for retrieving and manipulating JSON data.

    pop_after_processing : bool
        If True, the job will be popped from the queue after processing.
    """

    auto_convert_json_keys: bool = False
    auto_convert_json_keys: bool = False
    pop_after_processing: bool = False

    def __init__(
        self, auto_convert_json_keys: bool = False, pop_after_processing: bool = False
    ):
        self.auto_convert_json_keys = auto_convert_json_keys
        self.pop_after_processing = pop_after_processing

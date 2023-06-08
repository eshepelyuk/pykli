from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import completion_is_selected, is_searching, has_completions, Condition
from prompt_toolkit.application import get_app, run_in_terminal

def _is_complete(sql):
    # A complete command is an sql statement that ends with a semicolon, unless
    # there's an open quote surrounding it, as is common when writing a
    # CREATE FUNCTION command
    return sql.endswith(";") # and not is_open_quote(sql)

@Condition
def buffer_should_be_handled():
    doc = get_app().layout.get_buffer_by_name(DEFAULT_BUFFER).document
    text = doc.text.strip()

    return (
        text.startswith("\\")  # Special Command
        or text.endswith(r"\e")  # Special Command
        or text.endswith(r"\G")  # Ended with \e which should launch the editor
        or _is_complete(text)  # A complete SQL command
        or (text == "exit")  # Exit doesn't need semi-colon
        or (text == "quit")  # Quit doesn't need semi-colon
    )


def pykli_keys():

    kb = KeyBindings()

    @kb.add("enter", filter=completion_is_selected)
    def _(event):
        event.current_buffer.complete_state = None
        event.app.current_buffer.complete_state = None

    @kb.add("enter", filter=~(completion_is_selected | is_searching) & buffer_should_be_handled)
    def _(event):
        event.current_buffer.validate_and_handle()

    @kb.add("escape", filter=has_completions)
    def _(event):
        event.current_buffer.complete_state = None
        event.app.current_buffer.complete_state = None

    @kb.add("c-space")
    def _(event):
        b = event.app.current_buffer
        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=False)

    return kb

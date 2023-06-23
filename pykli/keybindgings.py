from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import completion_is_selected, is_searching, has_completions, Condition
from prompt_toolkit.application import get_app

@Condition
def should_handle_text():
    text = get_app().current_buffer.document.text.strip()
    return text.endswith(";") or text == "exit" or text == "quit" or text == ""


def pykli_keys():

    kb = KeyBindings()

    @kb.add("enter", filter=completion_is_selected)
    def _(event):
        event.current_buffer.complete_state = None
        event.app.current_buffer.complete_state = None

    @kb.add("enter", filter=~(completion_is_selected | is_searching) & should_handle_text)
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

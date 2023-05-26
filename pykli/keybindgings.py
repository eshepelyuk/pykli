from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import completion_is_selected, is_searching, has_completions

def pykli_keys():

    kb = KeyBindings()

    @kb.add("enter", filter=completion_is_selected)
    def _(event):
        event.current_buffer.complete_state = None
        event.app.current_buffer.complete_state = None

    # @kb.add("enter", filter=~(completion_is_selected | is_searching) & buffer_should_be_handled(pgcli))
    @kb.add("enter", filter=~(completion_is_selected | is_searching))
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

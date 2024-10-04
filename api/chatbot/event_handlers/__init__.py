import mesop as me
from app.api.chatbot.data_models import State

def on_click_show_modal(e: me.ClickEvent):
    """Opens modal to show generated code for the given model configuration."""
    print('option button clicked')
    state = me.state(State)
    state.modal_open = True
    
def on_click_modal(e: me.ClickEvent):
    """Allows modal to be closed."""
    state = me.state(State)
    if state.modal_open:
        state.modal_open = False
        
def on_knowledgebase_select(e: me.SelectSelectionChangeEvent):
    """Event to select model."""
    state = me.state(State)
    state.selected_model = e.value
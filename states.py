from aiogram.fsm.state import State, StatesGroup

class TranslationState(StatesGroup):
    waiting_for_text = State() # Состояние ожидание исходного текста
    waiting_for_iterations = State() # Состояние ожидания действий
    ready_for_repeat = State() # Состояние готовности к перезапуску
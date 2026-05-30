from collections import deque

TRACE_STORE = deque(maxlen=100)

def add_trace(trace_data: dict):
    TRACE_STORE.appendleft(trace_data)

def get_traces():
    return list(TRACE_STORE)
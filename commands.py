"""
Command Router — delegates to unified METIS command processor.
"""
from core.command_processor import processor


def process_command(command, confirm_callback=None, speak_callback=None, model=None):
    return processor.process(command, confirm_callback=confirm_callback, speak_callback=speak_callback, model=model)


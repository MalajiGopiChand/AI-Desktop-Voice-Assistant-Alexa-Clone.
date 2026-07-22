"""
Command Router — delegates to unified JARVIS command processor.
"""
from core.command_processor import processor


def process_command(command):
    return processor.process(command)

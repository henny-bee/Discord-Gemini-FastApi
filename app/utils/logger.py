import logging
import sys

def setup_logger():
    logger = logging.getLogger("discord_bot")
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    file_handler = logging.FileHandler("bot.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

def log_error(text: str, error_traceback: str, history: str = "N/A", 
              candidates: str = "N/A", parts: str = "N/A", prompt_feedbacks: str = "N/A") -> None:
    """Log errors to file for debugging."""
    with open('errors.log', 'a+', encoding='utf-8') as errorlog:
        errorlog.write('\n##########################\n')
        errorlog.write(f'Message: {text}\n')
        errorlog.write('-------------------\n')
        errorlog.write(f'Traceback:\n{error_traceback}\n')
        errorlog.write('-------------------\n')
        errorlog.write(f'History:\n{history}\n')
        errorlog.write('-------------------\n')
        errorlog.write(f'Candidates:\n{candidates}\n')
        errorlog.write('-------------------\n')
        errorlog.write(f'Parts:\n{parts}\n')
        errorlog.write('-------------------\n')
        errorlog.write(f'Prompt feedbacks:\n{prompt_feedbacks}\n')

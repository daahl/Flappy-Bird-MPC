def pid(y_target, y_current):
    """
    PID controller for the bird
    :return: Control action
    """
    error = y_target - y_current

    print(f"Error: {error}")
    
    return 1 if abs(error) > 0 else 0
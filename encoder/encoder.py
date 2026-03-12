import lgpio

class Encoder:

    __KP = 0.0005
    __DT = 0.05

    def __init__(self, aPin : int, aChip ) -> None:
        self.__pin = aPin
        self.__chip = aChip
        self.__pulse_count = 0
        
        lgpio.gpio_claim_alert(self.__chip, self.__pin, lgpio.BOTH_EDGES, lgpio.SET_PULL_UP) # claim the GPIO pin for input lgpio.gpio_set_mode(chip, pin, lgpio.GPIO_MODE_INPUT) # set the pin as input lgpio.gpio_set_pull(chip, pin, lgpio.GPIO_PULL_UP) # enable pull-up resistor lgpio.gpio_set_alert_func(chip, pin, count_pulse_callback) # set the interrupt handler for this pin
        lgpio.callback(self.__chip, self.__pin, lgpio.BOTH_EDGES, func=self.__count_pulse_callback) # register the callback function for both rising and falling edges

    # chip = gpiochip, gpio = pin number, level = 0 or 1, tick = timestamp of event
    def __count_pulse_callback(self, chip, gpio, level, tick) -> None:   # type: ignore
        self.__pulse_count += 1  # increment the pulse count for that motor
        
    def reset_count(self):
        self.__pulse_count = 0
        
    def pi_controller(self, target_rpm: int, current_throttle: float) -> float:
        current_rpm = (self.__pulse_count / 1080) * (60 / self.__DT)
        
        if target_rpm > 0:
            error = target_rpm - current_rpm
        elif target_rpm < 0:
            error = target_rpm + current_rpm
        else:
            error = 0
        
        adjustment = self.__KP * error
        
        new_throttle = max(-1.0, min(1.0, current_throttle + adjustment))

        print(f"__pulse_count: {self.__pulse_count}")
        print(f"error: {error}")
        self.reset_count()
        
        print(f"current_rpm: {current_rpm}")
        print(f"target_rpm: {target_rpm}")
        print(f"new_throttle: {new_throttle}")
        return new_throttle
    
        
     
        
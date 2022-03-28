from band_detection import BandDetectionResult
from detected_object import DetectedBand

COLOR_2_SIGNIFICANT = {
    'black_band':   0,
    'brown_band':   1,
    'red_band':     2,
    'orange_band':  3,
    'yellow_band':  4,
    'green_band':   5,
    'blue_band':    6,
    'violet_band':  7,
    'grey_band':    8,
    'white_band':   9,
    'gold_band':    None,
    'silver_band':  None,
}

COLOR_2_MULTIPLIER = {
    'black_band':   10**0,
    'brown_band':   10**1,
    'red_band':     10**2,
    'orange_band':  10**3,
    'yellow_band':  10**4,
    'green_band':   10**5,
    'blue_band':    10**6,
    'violet_band':  10**7,
    'grey_band':    10**8,
    'white_band':   10**9,
    'gold_band':    10**-1,
    'silver_band':  10**-2,
}

COLOR_2_TOLERANCE = {
    'black_band':   None,
    'brown_band':   1,
    'red_band':     2,
    'orange_band':  None,
    'yellow_band':  None,
    'green_band':   0.5,
    'blue_band':    0.25,
    'violet_band':  0.1,
    'grey_band':    0.05,
    'white_band':   None,
    'gold_band':    5,
    'silver_band':  10,
}

class ResistorError(Exception):
    def __init__(self, error_msg='The base class for resistor classification related errors'):
        super().__init__()
        self.error_msg = error_msg
    def __str__(self):
        return f'{type(self).__name__}: {self.error_msg}'

class UnstableBandDetectionError(ResistorError):
    def __init__(self, error_msg='The band detection result is not stable'):
        super().__init__(error_msg)

class InvalidSignificantError(ResistorError):
    def __init__(self, band: DetectedBand, error_msg='The given band is not a valid significant'):
        super().__init__(error_msg)
        self.band = band
        self.error_msg = f'"{self.band.label}" is not a valid significant'

class InvalidMultiplierError(ResistorError):
    def __init__(self, band: DetectedBand, error_msg='The given band is not a valid multiplier'):
        super().__init__(error_msg)
        self.band = band
        self.error_msg = f'"{self.band.label}" is not a valid multiplier'

class InvalidToleranceError(ResistorError):
    def __init__(self, band: DetectedBand, error_msg='The given band is not a valid tolerance'):
        super().__init__(error_msg)
        self.band = band
        self.error_msg = f'"{self.band.label}" is not a valid tolerance'

class Resistor:
    def __init__(self, bands: BandDetectionResult):
        """
        Initializes the Resistor object.
        Args:
            bands: The BandDetectionResult object to compute the resistance from.
        """
        if not bands.is_valid():
            raise UnstableBandDetectionError()
        self.bands = bands
    
    def get_resistance(self) -> int:
        """
        Computes the resistance represented by the resistor color bands.
        Returns:
            The computed resistance value.
        """
        significants = []
        for i in range(len(self.bands.detected_bands) - 2):
            value = COLOR_2_SIGNIFICANT[self.bands.detected_bands[i].label]
            if value is None:
                raise InvalidSignificantError(self.bands.detected_bands[i])
            significants.append(value)
        
        multiplier = COLOR_2_MULTIPLIER[self.bands.detected_bands[-2].label]
        if multiplier is None:
            raise InvalidMultiplierError(self.bands.detected_bands[-2])

        resistance = 0
        for i in range(len(significants)):
            resistance += significants[i] * 10**(len(significants)-i-1)
        resistance *= multiplier
        return resistance

    def get_tolerance(self) -> float:
        """
        Computes the tolerance represented by the resistor color bands.
        Returns:
            The computed tolerance value in percentage.
        """
        tolerance = COLOR_2_TOLERANCE[self.bands.detected_bands[-1].label]
        if tolerance is None:
            raise InvalidToleranceError(self.bands.detected_bands[-1])
        return tolerance

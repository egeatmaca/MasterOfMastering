DEFAULT_STEPS = ['normalization', 'equalization']

DEFAULT_SETTINGS = {
    'equalization': {
        'gain_adjustments': {
            1: 0.5,
            10: 0.5,
            100: 0.5,
            1000: 0.2,
            10000: -0.1
        }
    },
    'compression': {
        'threshold': 1.0,
        'ratio': 1.5
    }
}

PROFILES = {
    'default': {
        'equalization': {
            'target_band_energies': {
                1: 5,
                10: 5,
                100: 5,
                1000: 4,
                10000: 3,
            }
        }
    },
    'low': {
        'equalization': {
            'target_band_energies': {
                1: 5,
                10: 5,
                100: 5,
                1000: 3,
                10000: 2,
            }
        }
    },
    'mid': {
        'equalization': {
            'target_band_energies': {
                1: 2,
                10: 3,
                100: 4,
                1000: 5,
                10000: 4,
            }
        }
    },
    'high': {
        'equalization': {
            'target_band_energies': {
                1: 1,
                10: 2,
                100: 3,
                1000: 4,
                10000: 5,
            }
        }
    },
    'hard_bass': {
        'equalization': {
            'target_band_energies': {
                1: 5,
                10: 5,
                100: 5,
                1000: 2,
                10000: 1,
            }
        }
    },
}

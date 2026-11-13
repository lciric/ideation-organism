"""Why the preregistered design matters (preregistration, section 7).

On a simulated panel with no true size effect (the true slope of error on revision is the same for every
size of news) but with measurement error in the published consensus, defining 'large' by the size of the
revision itself creates a spurious positive interaction c, because it sorts on the noise the revision
shares with the error; defining 'large' by the lagged data surprise, as K20 does, does not. Fixed seed.
"""
import pytest

from snu import simulation

SEED = 20261113


@pytest.fixture(scope="module")
def scaled():
    return simulation.interaction_by_sort(simulation.simulate_panel(40000, SEED, "scaled"))


def test_revision_sort_creates_a_spurious_positive_interaction(scaled):
    c, se = scaled["revision_sort"]
    assert c > 0.04 and c / se > 4


def test_surprise_sort_does_not(scaled):
    c, se = scaled["surprise_sort"]
    assert abs(c) < 0.025 and abs(c / se) < 2
    assert scaled["revision_sort"][0] - c > 0.04


def test_noise_is_a_minor_part_of_the_revision():
    """About a tenth of the variance of the revision is consensus noise (the preregistration's central range
    is 0.02 to 0.12; its floor uses 0.20)."""
    assert 0.05 < simulation.noise_share() < 0.15


def test_with_noise_of_fixed_size_a_smaller_residual_remains_below_the_floor():
    """If the noise does not grow with turbulence, the surprise sort keeps the differential attenuation
    (section 7, effect 1), smaller than the revision sort's bias and below the preregistered floor 0.10."""
    res = simulation.interaction_by_sort(simulation.simulate_panel(40000, SEED, "fixed"))
    c_surprise, c_revision = res["surprise_sort"][0], res["revision_sort"][0]
    assert 0 < c_surprise < 0.10
    assert c_revision > c_surprise + 0.04

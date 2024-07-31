# pylint: disable=missing-function-docstring
import math
from typing import Tuple
import pytest
import torch
from torchgmm.bayes import MarkovChain


def test_fit_automatic_config():
    chain = MarkovChain()
    data = torch.randint(50, size=(100, 20))
    chain.fit(data)
    assert chain.model_.config.num_states == 50


@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_sample_and_fit():
    chain = MarkovChain(2)
    initial_probs, transition_probs = _set_probs(chain)
    sample = chain.sample(1000000, 10)

    new = MarkovChain(2)
    new.fit(sample)

    assert torch.allclose(initial_probs, new.model_.initial_probs, atol=1e-3)
    assert torch.allclose(transition_probs, new.model_.transition_probs, atol=1e-3)


def test_score():
    chain = MarkovChain(2)
    test_data, expected = _set_sample_data(chain)
    actual = chain.score(test_data)
    assert math.isclose(actual, -expected.mean())


def test_score_samples():
    chain = MarkovChain(2)
    test_data, expected = _set_sample_data(chain)
    actual = chain.score_samples(test_data)
    assert torch.allclose(actual, -expected)


# -------------------------------------------------------------------------------------------------


def _set_probs(chain: MarkovChain) -> Tuple[torch.Tensor, torch.Tensor]:
    data = torch.randint(2, size=(100, 20))
    chain.fit(data)

    initial_probs = torch.as_tensor([0.8, 0.2])
    chain.model_.initial_probs.copy_(initial_probs)

    transition_probs = torch.as_tensor([[0.5, 0.5], [0.1, 0.9]])
    chain.model_.transition_probs.copy_(transition_probs)

    return initial_probs, transition_probs


def _set_sample_data(chain: MarkovChain) -> Tuple[torch.Tensor, torch.Tensor]:
    _set_probs(chain)

    test_data = torch.as_tensor(
        [
            [1, 1, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
        ]
    )
    expected = torch.as_tensor(
        [
            math.log(0.2) + math.log(0.9) + math.log(0.1) + math.log(0.5),
            math.log(0.8) + math.log(0.5) + math.log(0.1) + math.log(0.5),
            math.log(0.8) + math.log(0.5) + math.log(0.5) + math.log(0.9),
        ]
    )
    return test_data, expected

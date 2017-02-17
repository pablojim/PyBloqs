import pandas as pd

from pybloqs.block.text import Span, Raw
from pybloqs.block.layout import Flow, HStack, VStack, Grid
from regression_framework import regression_test, update, skip_asserts


colors = ["Red", "Green", "Blue", "Magenta", "Orange", "Yellow", "Teal"]

frame = pd.DataFrame({"a": [1.11111111, 2.22222222, 3.33333333], "b": ["foo", "baz", "bar"]}, index=[1, 2, 3])
panel = pd.WidePanel({"a": frame, "b": frame})


def _construct_style_inheritance(cls, **kwargs):
    return cls([Raw(color, background_color=color) for color in colors], text_align="right", title="Layout", **kwargs)


def _construct_nested_layout(cls, **kwargs):
    with skip_asserts():
        sub_flow = test_flow()
        sub_hstack = test_hstack()
        sub_vstack = test_vstack()
        sub_grid = test_grid()

    return cls([sub_flow, sub_hstack, sub_vstack, sub_grid], **kwargs)


@regression_test
def test_flow():
    return Flow([Span(color, background_color=color) for color in colors], title="Flow Layout")


@regression_test
def test_flow_inherit_styles():
    return _construct_style_inheritance(Flow)


@regression_test
def test_flow_widepanel():
    return Flow(panel)


@regression_test
def test_flow_nested_combined_layouts():
    return _construct_nested_layout(Flow)


@regression_test
def test_hstack():
    return HStack([Raw(color, background_color=color) for color in colors], title="Horizontal Stack Layout")

@regression_test
def test_hstack_inherit_styles():
    return _construct_style_inheritance(HStack)


@regression_test
def test_hstack_widepanel():
    return HStack(panel)


@regression_test
def test_hstack_nested_combined_layouts():
    return _construct_nested_layout(HStack)


@regression_test
def test_vstack():
    return VStack([Raw(color, background_color=color) for color in colors], title="Vertical Stack Layout")


@regression_test
def test_vstack_inherit_styles():
    return _construct_style_inheritance(VStack)


@regression_test
def test_vstack_widepanel():
    return VStack(panel)


@regression_test
def test_vstack_nested_combined_layouts():
    return _construct_nested_layout(VStack)


@regression_test
def test_grid():
    return Grid([Raw(color, background_color=color) for color in colors], cols=3, title="Grid Layout")


@regression_test
def test_grid_inherit_styles():
    return _construct_style_inheritance(Grid, cols=3)


@regression_test
def test_grid_widepanel():
    return Grid(panel, cols=2)


@regression_test
def test_grid_nested_combined_layouts():
    return _construct_nested_layout(Grid, cols=2)


if __name__ == "__main__":
    update()
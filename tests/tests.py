from ..cs_mdoc_image_shift import parse_mdoc
from pathlib import Path

def test_parse_mdoc():
    result = parse_mdoc(Path('test.tif.mdoc'))
    assert isinstance(result, dict)
    # assert result['exposure'] == 'test.tif'
    assert result['x_shift'] == 0.948181
    assert result['y_shift'] == -2.61775
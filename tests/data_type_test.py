from logis.data_type import ConfigItem, SpatialProps


def test_config_item():
    cfg = ConfigItem(label="层高", key="height", value=100, value_type="int")

    assert cfg.value_type == "int"


def test_spatial_props():
    props = SpatialProps.model_validate(
        dict(
            层高=dict(quantity=100),
            width=dict(quantity=100),
            centerPoint=dict(x=1, y=None, z=9.0),
        )
    )

    assert props.height.value == 100
    assert props.width.value == 100
    assert props.depth is None
    assert props.center_point.z == 9.0

    dc = props.model_dump()
    print(dc)

    props = SpatialProps.model_validate(dc)
    assert props.center_point.z == 9.0

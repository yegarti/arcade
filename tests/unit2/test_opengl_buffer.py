from array import array
import pytest


def test_properties(ctx):
    buffer = ctx.buffer(data=b'Hello world')
    assert buffer.glo.value > 0
    assert buffer.ctx == ctx


def test_create_empty(ctx):
    with pytest.raises(ValueError):
        ctx.buffer()


def test_read_write(ctx):
    buffer = ctx.buffer(data=b'Hello world')
    assert buffer.read() == b'Hello world'
    assert buffer.read(size=5) == b'Hello'
    assert buffer.read(size=5, offset=6) == b'world'

    # Reading outside buffer by 1 byte
    with pytest.raises(ValueError):
        buffer.read(size=12)

    # Reading outside buffer by 1 byte with offset
    with pytest.raises(ValueError):
        buffer.read(size=6, offset=6)

    # Read with zero or negative size
    with pytest.raises(ValueError):
        buffer.read(0)


def test_write_bufferprotocol(ctx):
    """Write data to buffer with buffer protocol"""
    data = array('f', [1, 2, 3, 4])
    buff = ctx.buffer(data=data)
    assert buff.read() == data.tobytes()


def test_orphan(ctx):
    buffer = ctx.buffer(data=b'Hello world')
    buffer.orphan(size=20)
    assert buffer.size == 20
    assert len(buffer.read()) == 20

    buffer.write(b'Testing')
    assert buffer.read(size=7) == b'Testing'
    buffer.write(b'Testing', offset=10)
    assert buffer.read(offset=10, size=7) == b'Testing'

    buffer.orphan(double=True)
    assert buffer.size == 40


def test_copy(ctx):
    buffer = ctx.buffer(data=b'Hello world')
    source = ctx.buffer(reserve=20)
    buffer.copy_from_buffer(source, size=10, offset=0)
    # Copy out of bounds in the source buffer
    with pytest.raises(ValueError):
        buffer.copy_from_buffer(source, size=10, source_offset=15)

    # Copy out of bounds in the destination buffer
    with pytest.raises(ValueError):
        buffer.copy_from_buffer(source, size=10, offset=15)

from mads.build import shell, proc


def test_shell():
    """Test that shell returns stdout"""

    result = shell("echo hello")
    assert result == "hello"


def test_shell_stdin():
    """Test that shell accepts stdin"""

    result = shell("cat", input="hello")
    assert result == "hello"


def test_shell_cwd():
    """Test that shell accepts cwd"""

    result = shell("pwd -P", cwd="/")
    assert result == "/"


def test_proc():
    """Test that proc returns a completed process"""

    result = proc("echo hello")
    assert result.returncode == 0

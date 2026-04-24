import pytest
import time
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def reset_monitor():
    """Reset monitor state between tests."""
    import vibe.terminal_monitor as m
    m._monitored.clear()
    m._terminal_alerts.clear()
    yield
    m._monitored.clear()
    m._terminal_alerts.clear()


def test_register_and_get_panes():
    from vibe.terminal_monitor import register_pane, get_panes
    register_pane('work:0.0', label='mira claude')
    panes = get_panes()
    assert len(panes) == 1
    assert panes[0]['target'] == 'work:0.0'
    assert panes[0]['label'] == 'mira claude'
    assert panes[0]['auto'] is False


def test_unregister_pane():
    from vibe.terminal_monitor import register_pane, unregister_pane, get_panes
    register_pane('work:0.0', label='test')
    unregister_pane('work:0.0')
    assert get_panes() == []


def test_auto_discover_adds_claude_panes():
    fake_panes = [
        {'target': 'work:0.0', 'command': 'ccc', 'cwd': '/Users/chao/projects/mira', 'session': 'work', 'window': 0, 'pane': 0},
        {'target': 'work:0.1', 'command': 'node', 'cwd': '/Users/chao/projects/foo', 'session': 'work', 'window': 0, 'pane': 1},
    ]
    with patch('vibe.tmux_bridge.list_panes', return_value=fake_panes), \
         patch('vibe.tmux_bridge.capture_pane', return_value='some output'):
        from vibe.terminal_monitor import _poll_once
        _poll_once()

    from vibe.terminal_monitor import get_panes
    panes = get_panes()
    targets = [p['target'] for p in panes]
    assert 'work:0.0' in targets   # ccc → auto-discovered
    assert 'work:0.1' not in targets  # node → ignored


def test_keyword_detection_creates_alert():
    import vibe.terminal_monitor as m
    m._monitored['work:0.0'] = {
        'target': 'work:0.0', 'label': 'claude/mira', 'command': 'ccc',
        'cwd': '/tmp', 'auto': True, 'project_id': None,
        'last_output': '', 'waiting': False, 'registered_at': time.time(),
    }
    output_with_prompt = "Processing files...\nDo you want to proceed? (y/n)"
    with patch('vibe.tmux_bridge.list_panes', return_value=[]), \
         patch('vibe.tmux_bridge.capture_pane', return_value=output_with_prompt):
        from vibe.terminal_monitor import _poll_once
        _poll_once()

    assert m._monitored['work:0.0']['waiting'] is True
    alerts = m._terminal_alerts
    assert len(alerts) == 1
    assert alerts[0]['target'] == 'work:0.0'


def test_get_terminal_alerts_clears_queue():
    import vibe.terminal_monitor as m
    m._terminal_alerts.append({'target': 'x', 'label': 'x', 'snippet': 'x', 'ts': 0})
    from vibe.terminal_monitor import get_terminal_alerts
    alerts = get_terminal_alerts()
    assert len(alerts) == 1
    assert m._terminal_alerts == []


def test_waiting_cleared_when_prompt_gone():
    import vibe.terminal_monitor as m
    m._monitored['work:0.0'] = {
        'target': 'work:0.0', 'label': 'claude/mira', 'command': 'ccc',
        'cwd': '/tmp', 'auto': True, 'project_id': None,
        'last_output': 'Do you want to proceed? (y/n)',
        'waiting': True, 'registered_at': time.time(),
    }
    clean_output = "Proceeding with operation...\nDone."
    with patch('vibe.tmux_bridge.list_panes', return_value=[]), \
         patch('vibe.tmux_bridge.capture_pane', return_value=clean_output):
        from vibe.terminal_monitor import _poll_once
        _poll_once()

    assert m._monitored['work:0.0']['waiting'] is False

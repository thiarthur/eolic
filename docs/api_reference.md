# API Reference

## Eolic

### `__init__(self, remote_targets: List[Any]) -> None`

Initialize Eolic with an optional list of remote targets.

### `register_target(self, target: Any) -> None`

Register a new remote target.

### `register_listener(self, event: Any, fn: Callable[..., None]) -> None`

Register a new event listener.

### `on(self, event: Any) -> Callable`

Decorator to register an event listener.

### `emit(self, event: Any, *args, **kwargs) -> None`

Emit an event to all registered listeners and remote targets.

## EventRemoteTargetHandler

### `register(self, target: Any) -> None`

Register a remote target.

### `emit(self, event: Any, *args, **kwargs) -> None`

Emit an event to all registered remote targets.

## EventListenerHandler

### `register(self, event: Any, fn: Callable[..., None]) -> None`

Register a new event listener.

### `_listener_map`

Dictionary mapping events to listeners.

## EventRemoteDispatcherFactory

### `create(self, target: EventRemoteTarget) -> EventRemoteDispatcher`

Create an appropriate dispatcher based on the target type.

## EventRemoteURLDispatcher

### `__init__(self, target: EventRemoteTarget) -> None`

Initialize the dispatcher with the given target.

### `dispatch(self, event: Any, *args, **kwargs) -> None`

Dispatch the event to the remote target.

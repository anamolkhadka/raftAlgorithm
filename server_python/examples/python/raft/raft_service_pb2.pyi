from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RequestVoteRequest(_message.Message):
    __slots__ = ("term", "candidateId", "lastLogIndex", "lastLogTerm")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidateId: int
    lastLogIndex: int
    lastLogTerm: int
    def __init__(self, term: _Optional[int] = ..., candidateId: _Optional[int] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class RequestVoteResponse(_message.Message):
    __slots__ = ("term", "voteGranted")
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTEGRANTED_FIELD_NUMBER: _ClassVar[int]
    term: int
    voteGranted: bool
    def __init__(self, term: _Optional[int] = ..., voteGranted: bool = ...) -> None: ...

class AppendEntriesRequest(_message.Message):
    __slots__ = ("term", "leaderId", "entries", "prevLogIndex", "prevLogTerm", "leaderCommit")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    PREVLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    PREVLOGTERM_FIELD_NUMBER: _ClassVar[int]
    LEADERCOMMIT_FIELD_NUMBER: _ClassVar[int]
    term: int
    leaderId: int
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    prevLogIndex: int
    prevLogTerm: int
    leaderCommit: int
    def __init__(self, term: _Optional[int] = ..., leaderId: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., prevLogIndex: _Optional[int] = ..., prevLogTerm: _Optional[int] = ..., leaderCommit: _Optional[int] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ("term", "success")
    TERM_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    term: int
    success: bool
    def __init__(self, term: _Optional[int] = ..., success: bool = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("index", "term", "command")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    index: int
    term: int
    command: str
    def __init__(self, index: _Optional[int] = ..., term: _Optional[int] = ..., command: _Optional[str] = ...) -> None: ...

class ClientRequestMessage(_message.Message):
    __slots__ = ("command",)
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    command: str
    def __init__(self, command: _Optional[str] = ...) -> None: ...

class ClientResponseMessage(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

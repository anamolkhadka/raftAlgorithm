# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: raft_service.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'raft_service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12raft_service.proto\x12\x04raft\"b\n\x12RequestVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0b\x63\x61ndidateId\x18\x02 \x01(\x05\x12\x14\n\x0clastLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0blastLogTerm\x18\x04 \x01(\x05\"8\n\x13RequestVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0bvoteGranted\x18\x02 \x01(\x08\"\x98\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x10\n\x08leaderId\x18\x02 \x01(\x05\x12\x1f\n\x07\x65ntries\x18\x03 \x03(\x0b\x32\x0e.raft.LogEntry\x12\x14\n\x0cprevLogIndex\x18\x04 \x01(\x05\x12\x13\n\x0bprevLogTerm\x18\x05 \x01(\x05\x12\x14\n\x0cleaderCommit\x18\x06 \x01(\x05\"6\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\"8\n\x08LogEntry\x12\r\n\x05index\x18\x01 \x01(\x05\x12\x0c\n\x04term\x18\x02 \x01(\x05\x12\x0f\n\x07\x63ommand\x18\x03 \x01(\t\"\'\n\x14\x43lientRequestMessage\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\"9\n\x15\x43lientResponseMessage\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\xe5\x01\n\x0bRaftService\x12\x42\n\x0bRequestVote\x12\x18.raft.RequestVoteRequest\x1a\x19.raft.RequestVoteResponse\x12H\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequest\x1a\x1b.raft.AppendEntriesResponse\x12H\n\rClientRequest\x12\x1a.raft.ClientRequestMessage\x1a\x1b.raft.ClientResponseMessageb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REQUESTVOTEREQUEST']._serialized_start=28
  _globals['_REQUESTVOTEREQUEST']._serialized_end=126
  _globals['_REQUESTVOTERESPONSE']._serialized_start=128
  _globals['_REQUESTVOTERESPONSE']._serialized_end=184
  _globals['_APPENDENTRIESREQUEST']._serialized_start=187
  _globals['_APPENDENTRIESREQUEST']._serialized_end=339
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=341
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=395
  _globals['_LOGENTRY']._serialized_start=397
  _globals['_LOGENTRY']._serialized_end=453
  _globals['_CLIENTREQUESTMESSAGE']._serialized_start=455
  _globals['_CLIENTREQUESTMESSAGE']._serialized_end=494
  _globals['_CLIENTRESPONSEMESSAGE']._serialized_start=496
  _globals['_CLIENTRESPONSEMESSAGE']._serialized_end=553
  _globals['_RAFTSERVICE']._serialized_start=556
  _globals['_RAFTSERVICE']._serialized_end=785
# @@protoc_insertion_point(module_scope)
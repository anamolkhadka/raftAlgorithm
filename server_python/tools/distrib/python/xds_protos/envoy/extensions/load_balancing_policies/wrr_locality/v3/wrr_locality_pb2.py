# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: envoy/extensions/load_balancing_policies/wrr_locality/v3/wrr_locality.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from envoy.config.cluster.v3 import cluster_pb2 as envoy_dot_config_dot_cluster_dot_v3_dot_cluster__pb2
from udpa.annotations import status_pb2 as udpa_dot_annotations_dot_status__pb2
from validate import validate_pb2 as validate_dot_validate__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\nKenvoy/extensions/load_balancing_policies/wrr_locality/v3/wrr_locality.proto\x12\x38\x65nvoy.extensions.load_balancing_policies.wrr_locality.v3\x1a%envoy/config/cluster/v3/cluster.proto\x1a\x1dudpa/annotations/status.proto\x1a\x17validate/validate.proto\"f\n\x0bWrrLocality\x12W\n\x17\x65ndpoint_picking_policy\x18\x01 \x01(\x0b\x32,.envoy.config.cluster.v3.LoadBalancingPolicyB\x08\xfa\x42\x05\x8a\x01\x02\x10\x01\x42\xd4\x01\nFio.envoyproxy.envoy.extensions.load_balancing_policies.wrr_locality.v3B\x10WrrLocalityProtoP\x01Zngithub.com/envoyproxy/go-control-plane/envoy/extensions/load_balancing_policies/wrr_locality/v3;wrr_localityv3\xba\x80\xc8\xd1\x06\x02\x10\x02\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'envoy.extensions.load_balancing_policies.wrr_locality.v3.wrr_locality_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\nFio.envoyproxy.envoy.extensions.load_balancing_policies.wrr_locality.v3B\020WrrLocalityProtoP\001Zngithub.com/envoyproxy/go-control-plane/envoy/extensions/load_balancing_policies/wrr_locality/v3;wrr_localityv3\272\200\310\321\006\002\020\002'
  _WRRLOCALITY.fields_by_name['endpoint_picking_policy']._options = None
  _WRRLOCALITY.fields_by_name['endpoint_picking_policy']._serialized_options = b'\372B\005\212\001\002\020\001'
  _globals['_WRRLOCALITY']._serialized_start=232
  _globals['_WRRLOCALITY']._serialized_end=334
# @@protoc_insertion_point(module_scope)

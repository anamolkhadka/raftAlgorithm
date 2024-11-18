# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: xds/data/orca/v3/orca_load_report.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from validate import validate_pb2 as validate_dot_validate__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'xds/data/orca/v3/orca_load_report.proto\x12\x10xds.data.orca.v3\x1a\x17validate/validate.proto\"\x89\x05\n\x0eOrcaLoadReport\x12\'\n\x0f\x63pu_utilization\x18\x01 \x01(\x01\x42\x0e\xfa\x42\x0b\x12\t)\x00\x00\x00\x00\x00\x00\x00\x00\x12\x30\n\x0fmem_utilization\x18\x02 \x01(\x01\x42\x17\xfa\x42\x14\x12\x12\x19\x00\x00\x00\x00\x00\x00\xf0?)\x00\x00\x00\x00\x00\x00\x00\x00\x12\x0f\n\x03rps\x18\x03 \x01(\x04\x42\x02\x18\x01\x12G\n\x0crequest_cost\x18\x04 \x03(\x0b\x32\x31.xds.data.orca.v3.OrcaLoadReport.RequestCostEntry\x12\x64\n\x0butilization\x18\x05 \x03(\x0b\x32\x31.xds.data.orca.v3.OrcaLoadReport.UtilizationEntryB\x1c\xfa\x42\x19\x9a\x01\x16*\x14\x12\x12\x19\x00\x00\x00\x00\x00\x00\xf0?)\x00\x00\x00\x00\x00\x00\x00\x00\x12&\n\x0erps_fractional\x18\x06 \x01(\x01\x42\x0e\xfa\x42\x0b\x12\t)\x00\x00\x00\x00\x00\x00\x00\x00\x12\x1b\n\x03\x65ps\x18\x07 \x01(\x01\x42\x0e\xfa\x42\x0b\x12\t)\x00\x00\x00\x00\x00\x00\x00\x00\x12I\n\rnamed_metrics\x18\x08 \x03(\x0b\x32\x32.xds.data.orca.v3.OrcaLoadReport.NamedMetricsEntry\x12/\n\x17\x61pplication_utilization\x18\t \x01(\x01\x42\x0e\xfa\x42\x0b\x12\t)\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x32\n\x10RequestCostEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x01:\x02\x38\x01\x1a\x32\n\x10UtilizationEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x01:\x02\x38\x01\x1a\x33\n\x11NamedMetricsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x01:\x02\x38\x01\x42]\n\x1b\x63om.github.xds.data.orca.v3B\x13OrcaLoadReportProtoP\x01Z\'github.com/cncf/xds/go/xds/data/orca/v3b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'xds.data.orca.v3.orca_load_report_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\033com.github.xds.data.orca.v3B\023OrcaLoadReportProtoP\001Z\'github.com/cncf/xds/go/xds/data/orca/v3'
  _ORCALOADREPORT_REQUESTCOSTENTRY._options = None
  _ORCALOADREPORT_REQUESTCOSTENTRY._serialized_options = b'8\001'
  _ORCALOADREPORT_UTILIZATIONENTRY._options = None
  _ORCALOADREPORT_UTILIZATIONENTRY._serialized_options = b'8\001'
  _ORCALOADREPORT_NAMEDMETRICSENTRY._options = None
  _ORCALOADREPORT_NAMEDMETRICSENTRY._serialized_options = b'8\001'
  _ORCALOADREPORT.fields_by_name['cpu_utilization']._options = None
  _ORCALOADREPORT.fields_by_name['cpu_utilization']._serialized_options = b'\372B\013\022\t)\000\000\000\000\000\000\000\000'
  _ORCALOADREPORT.fields_by_name['mem_utilization']._options = None
  _ORCALOADREPORT.fields_by_name['mem_utilization']._serialized_options = b'\372B\024\022\022\031\000\000\000\000\000\000\360?)\000\000\000\000\000\000\000\000'
  _ORCALOADREPORT.fields_by_name['rps']._options = None
  _ORCALOADREPORT.fields_by_name['rps']._serialized_options = b'\030\001'
  _ORCALOADREPORT.fields_by_name['utilization']._options = None
  _ORCALOADREPORT.fields_by_name['utilization']._serialized_options = b'\372B\031\232\001\026*\024\022\022\031\000\000\000\000\000\000\360?)\000\000\000\000\000\000\000\000'
  _ORCALOADREPORT.fields_by_name['rps_fractional']._options = None
  _ORCALOADREPORT.fields_by_name['rps_fractional']._serialized_options = b'\372B\013\022\t)\000\000\000\000\000\000\000\000'
  _ORCALOADREPORT.fields_by_name['eps']._options = None
  _ORCALOADREPORT.fields_by_name['eps']._serialized_options = b'\372B\013\022\t)\000\000\000\000\000\000\000\000'
  _ORCALOADREPORT.fields_by_name['application_utilization']._options = None
  _ORCALOADREPORT.fields_by_name['application_utilization']._serialized_options = b'\372B\013\022\t)\000\000\000\000\000\000\000\000'
  _globals['_ORCALOADREPORT']._serialized_start=87
  _globals['_ORCALOADREPORT']._serialized_end=736
  _globals['_ORCALOADREPORT_REQUESTCOSTENTRY']._serialized_start=581
  _globals['_ORCALOADREPORT_REQUESTCOSTENTRY']._serialized_end=631
  _globals['_ORCALOADREPORT_UTILIZATIONENTRY']._serialized_start=633
  _globals['_ORCALOADREPORT_UTILIZATIONENTRY']._serialized_end=683
  _globals['_ORCALOADREPORT_NAMEDMETRICSENTRY']._serialized_start=685
  _globals['_ORCALOADREPORT_NAMEDMETRICSENTRY']._serialized_end=736
# @@protoc_insertion_point(module_scope)

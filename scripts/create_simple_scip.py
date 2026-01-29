"""
创建 test_simple.scip - 基本符号、定义、引用测试

文件包含：
- 2 个文档（main.py, utils.py）
- 5 个符号定义
- 2 个符号有引用（MyClass.methodA 引用 utils.helper，main 引用 common.logger 3 次）
- 各种符号角色：Definition, Reference, ReadAccess, WriteAccess
"""

from scip_parser.proto import scip_pb2


def create_test_simple():
    pb_index = scip_pb2.Index()

    # Metadata
    pb_index.metadata.version = 1
    pb_index.metadata.tool_info.name = "scip-python"
    pb_index.metadata.tool_info.version = "0.1.0"
    pb_index.metadata.project_root = "/test/project"
    pb_index.metadata.text_document_encoding = scip_pb2.UTF8

    # Document 1: main.py
    doc_main = pb_index.documents.add()
    doc_main.relative_path = "main.py"
    doc_main.language = "python"

    # Symbol: main()
    occ_main_def = doc_main.occurrences.add()
    occ_main_def.symbol = "python test-project main#main()."
    occ_main_def.range.extend([0, 0, 10, 0])
    occ_main_def.symbol_roles = scip_pb2.Definition

    sym_main = doc_main.symbols.add()
    sym_main.symbol = "python test-project main#main()."
    sym_main.display_name = "main"
    sym_main.kind = scip_pb2.SymbolInformation.Function
    sym_main.documentation.extend(["Main function"])

    # Occurrence: 调用 MyClass.methodA
    occ_method_call = doc_main.occurrences.add()
    occ_method_call.symbol = "python test-project myclass/MyClass#methodA()."
    occ_method_call.range.extend([3, 4, 3, 20])
    occ_method_call.symbol_roles = scip_pb2.ReadAccess

    # Occurrence: 读取 common.logger（第 1 次）
    occ_logger_read1 = doc_main.occurrences.add()
    occ_logger_read1.symbol = "python test-project common#logger."
    occ_logger_read1.range.extend([5, 2, 5, 9])
    occ_logger_read1.symbol_roles = scip_pb2.ReadAccess

    # Occurrence: 读取 common.logger（第 2 次）
    occ_logger_read2 = doc_main.occurrences.add()
    occ_logger_read2.symbol = "python test-project common#logger."
    occ_logger_read2.range.extend([7, 2, 7, 9])
    occ_logger_read2.symbol_roles = scip_pb2.ReadAccess

    # Occurrence: 读取 common.logger（第 3 次）
    occ_logger_read3 = doc_main.occurrences.add()
    occ_logger_read3.symbol = "python test-project common#logger."
    occ_logger_read3.range.extend([9, 2, 9, 9])
    occ_logger_read3.symbol_roles = scip_pb2.ReadAccess

    # Document 2: utils.py
    doc_utils = pb_index.documents.add()
    doc_utils.relative_path = "utils.py"
    doc_utils.language = "python"

    # Symbol: helper()
    occ_helper_def = doc_utils.occurrences.add()
    occ_helper_def.symbol = "python test-project utils/helper#helper()."
    occ_helper_def.range.extend([0, 0, 10, 0])
    occ_helper_def.symbol_roles = scip_pb2.Definition

    sym_helper = doc_utils.symbols.add()
    sym_helper.symbol = "python test-project utils/helper#helper()."
    sym_helper.display_name = "helper"
    sym_helper.kind = scip_pb2.SymbolInformation.Function
    sym_helper.documentation.extend(["Helper function"])

    # Occurrence: 被 MyClass.methodA 引用
    occ_helper_ref = doc_utils.occurrences.add()
    occ_helper_ref.symbol = "python test-project myclass/MyClass#methodA()."
    occ_helper_ref.range.extend([5, 4, 5, 12])
    occ_helper_ref.symbol_roles = scip_pb2.ReadAccess

    # Document 3: common.py
    doc_common = pb_index.documents.add()
    doc_common.relative_path = "common.py"
    doc_common.language = "python"

    # Symbol: logger
    occ_logger_def = doc_common.occurrences.add()
    occ_logger_def.symbol = "python test-project common#logger."
    occ_logger_def.range.extend([0, 0, 5, 0])
    occ_logger_def.symbol_roles = scip_pb2.Definition

    sym_logger = doc_common.symbols.add()
    sym_logger.symbol = "python test-project common#logger."
    sym_logger.display_name = "logger"
    sym_logger.kind = scip_pb2.SymbolInformation.Variable
    sym_logger.documentation.extend(["Logger instance"])

    # Document 4: myclass.py
    doc_myclass = pb_index.documents.add()
    doc_myclass.relative_path = "myclass.py"
    doc_myclass.language = "python"

    # Symbol: MyClass
    occ_class_def = doc_myclass.occurrences.add()
    occ_class_def.symbol = "python test-project myclass/MyClass#"
    occ_class_def.range.extend([0, 0, 20, 0])
    occ_class_def.symbol_roles = scip_pb2.Definition

    sym_class = doc_myclass.symbols.add()
    sym_class.symbol = "python test-project myclass/MyClass#"
    sym_class.display_name = "MyClass"
    sym_class.kind = scip_pb2.SymbolInformation.Class
    sym_class.documentation.extend(["A class"])

    # Symbol: methodA
    occ_method_def = doc_myclass.occurrences.add()
    occ_method_def.symbol = "python test-project myclass/MyClass#methodA()."
    occ_method_def.range.extend([5, 0, 25, 0])
    occ_method_def.symbol_roles = scip_pb2.Definition

    sym_method = doc_myclass.symbols.add()
    sym_method.symbol = "python test-project myclass/MyClass#methodA()."
    sym_method.display_name = "methodA"
    sym_method.kind = scip_pb2.SymbolInformation.Method
    sym_method.documentation.extend(["Method A"])

    # Occurrence: methodA 调用 utils.helper
    occ_method_call_helper = doc_myclass.occurrences.add()
    occ_method_call_helper.symbol = "python test-project utils/helper#helper()."
    occ_method_call_helper.range.extend([10, 8, 10, 16])
    occ_method_call_helper.symbol_roles = scip_pb2.ReadAccess

    # Occurrence: methodA 写入 common.logger
    occ_method_write = doc_myclass.occurrences.add()
    occ_method_write.symbol = "python test-project common#logger."
    occ_method_write.range.extend([15, 8, 15, 15])
    occ_method_write.symbol_roles = scip_pb2.WriteAccess

    # 保存
    with open("tests/fixtures/test_simple.scip", "wb") as f:
        f.write(pb_index.SerializeToString())

    print("Created tests/fixtures/test_simple.scip")
    print(f"  - Documents: {len(pb_index.documents)}")
    print(f"  - Symbols: {sum(len(d.symbols) for d in pb_index.documents)}")
    print(f"  - Total occurrences: {sum(len(d.occurrences) for d in pb_index.documents)}")


if __name__ == "__main__":
    create_test_simple()

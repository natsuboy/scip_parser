"""
创建 test_call_graph.scip - 函数调用关系测试

文件包含：
- 1 个文档（app.py）
- 4 个函数（main, processA, processB, helper）
- 2 条调用链：main -> processA -> helper, main -> processB -> helper
"""

from scip_parser.proto import scip_pb2


def create_test_call_graph():
    pb_index = scip_pb2.Index()

    # Metadata
    pb_index.metadata.version = 1
    pb_index.metadata.tool_info.name = "scip-python"
    pb_index.metadata.tool_info.version = "0.1.0"
    pb_index.metadata.project_root = "/test/project"

    # Document: app.py
    doc = pb_index.documents.add()
    doc.relative_path = "app.py"
    doc.language = "python"

    # Symbol: main() 函数（第 0-10 行）
    occ_main_def = doc.occurrences.add()
    occ_main_def.symbol = "python test-project app#main()."
    occ_main_def.range.extend([0, 0, 10, 0])
    occ_main_def.symbol_roles = scip_pb2.Definition
    occ_main_def.enclosing_range.extend([0, 0, 10, 0])

    sym_main = doc.symbols.add()
    sym_main.symbol = "python test-project app#main()."
    sym_main.display_name = "main"
    sym_main.kind = scip_pb2.SymbolInformation.Function
    sym_main.documentation.extend(["Main entry point"])

    # Occurrence: main 调用 processA（第 3 行）
    occ_call_a = doc.occurrences.add()
    occ_call_a.symbol = "python test-project app/processA()."
    occ_call_a.range.extend([3, 4, 3, 12])
    occ_call_a.symbol_roles = scip_pb2.ReadAccess
    occ_call_a.enclosing_range.extend([0, 0, 10, 0])

    # Occurrence: main 调用 processB（第 5 行）
    occ_call_b = doc.occurrences.add()
    occ_call_b.symbol = "python test-project app/processB()."
    occ_call_b.range.extend([5, 4, 5, 12])
    occ_call_b.symbol_roles = scip_pb2.ReadAccess
    occ_call_b.enclosing_range.extend([0, 0, 10, 0])

    # Symbol: processA() 函数（第 12-20 行）
    occ_process_a_def = doc.occurrences.add()
    occ_process_a_def.symbol = "python test-project app/processA()."
    occ_process_a_def.range.extend([12, 0, 20, 0])
    occ_process_a_def.symbol_roles = scip_pb2.Definition
    occ_process_a_def.enclosing_range.extend([12, 0, 20, 0])

    sym_process_a = doc.symbols.add()
    sym_process_a.symbol = "python test-project app/processA()."
    sym_process_a.display_name = "processA"
    sym_process_a.kind = scip_pb2.SymbolInformation.Function
    sym_process_a.documentation.extend(["Process A"])

    # Occurrence: processA 调用 helper（第 15 行）
    occ_call_helper1 = doc.occurrences.add()
    occ_call_helper1.symbol = "python test-project app/helper()."
    occ_call_helper1.range.extend([15, 8, 15, 16])
    occ_call_helper1.symbol_roles = scip_pb2.ReadAccess
    occ_call_helper1.enclosing_range.extend([12, 0, 20, 0])

    # Symbol: processB() 函数（第 22-30 行）
    occ_process_b_def = doc.occurrences.add()
    occ_process_b_def.symbol = "python test-project app/processB()."
    occ_process_b_def.range.extend([22, 0, 30, 0])
    occ_process_b_def.symbol_roles = scip_pb2.Definition
    occ_process_b_def.enclosing_range.extend([22, 0, 30, 0])

    sym_process_b = doc.symbols.add()
    sym_process_b.symbol = "python test-project app/processB()."
    sym_process_b.display_name = "processB"
    sym_process_b.kind = scip_pb2.SymbolInformation.Function
    sym_process_b.documentation.extend(["Process B"])

    # Occurrence: processB 调用 helper（第 25 行）
    occ_call_helper2 = doc.occurrences.add()
    occ_call_helper2.symbol = "python test-project app/helper()."
    occ_call_helper2.range.extend([25, 8, 25, 16])
    occ_call_helper2.symbol_roles = scip_pb2.ReadAccess
    occ_call_helper2.enclosing_range.extend([22, 0, 30, 0])

    # Symbol: helper() 函数（第 32-40 行）
    occ_helper_def = doc.occurrences.add()
    occ_helper_def.symbol = "python test-project app/helper()."
    occ_helper_def.range.extend([32, 0, 40, 0])
    occ_helper_def.symbol_roles = scip_pb2.Definition
    occ_helper_def.enclosing_range.extend([32, 0, 40, 0])

    sym_helper = doc.symbols.add()
    sym_helper.symbol = "python test-project app/helper()."
    sym_helper.display_name = "helper"
    sym_helper.kind = scip_pb2.SymbolInformation.Function
    sym_helper.documentation.extend(["Helper function"])

    # 保存
    with open("tests/fixtures/test_call_graph.scip", "wb") as f:
        f.write(pb_index.SerializeToString())

    print("Created tests/fixtures/test_call_graph.scip")


if __name__ == "__main__":
    create_test_call_graph()

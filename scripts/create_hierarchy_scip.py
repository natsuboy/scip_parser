"""
创建 test_hierarchy.scip - 接口实现、继承关系测试

文件包含：
- 1 个文档（shapes.py）
- 1 个接口（Shape）
- 2 个实现类（Circle, Rectangle）
- Relationship: 实现关系
"""

from scip_parser.proto import scip_pb2


def create_test_hierarchy():
    pb_index = scip_pb2.Index()

    # Metadata
    pb_index.metadata.version = 1
    pb_index.metadata.tool_info.name = "scip-python"
    pb_index.metadata.tool_info.version = "0.1.0"
    pb_index.metadata.project_root = "/test/project"

    # Document: shapes.py
    doc = pb_index.documents.add()
    doc.relative_path = "shapes.py"
    doc.language = "python"

    # Symbol: Shape 接口
    occ_shape_def = doc.occurrences.add()
    occ_shape_def.symbol = "python test-project shapes/Shape#"
    occ_shape_def.range.extend([0, 0, 15, 0])
    occ_shape_def.symbol_roles = scip_pb2.Definition

    sym_shape = doc.symbols.add()
    sym_shape.symbol = "python test-project shapes/Shape#"
    sym_shape.display_name = "Shape"
    sym_shape.kind = scip_pb2.SymbolInformation.Interface
    sym_shape.documentation.extend(["Base shape interface"])

    # Symbol: Shape.area() 方法
    occ_area_def = doc.occurrences.add()
    occ_area_def.symbol = "python test-project shapes/Shape#area()."
    occ_area_def.range.extend([5, 4, 25, 0])
    occ_area_def.symbol_roles = scip_pb2.Definition

    sym_area = doc.symbols.add()
    sym_area.symbol = "python test-project shapes/Shape#area()."
    sym_area.display_name = "area"
    sym_area.kind = scip_pb2.SymbolInformation.Method
    sym_area.documentation.extend(["Calculate area"])

    # Symbol: Circle 类（实现 Shape）
    occ_circle_def = doc.occurrences.add()
    occ_circle_def.symbol = "python test-project shapes/Circle#"
    occ_circle_def.range.extend([30, 0, 50, 0])
    occ_circle_def.symbol_roles = scip_pb2.Definition

    sym_circle = doc.symbols.add()
    sym_circle.symbol = "python test-project shapes/Circle#"
    sym_circle.display_name = "Circle"
    sym_circle.kind = scip_pb2.SymbolInformation.Class
    sym_circle.documentation.extend(["Circle shape"])

    # Relationship: Circle 实现了 Shape
    rel_circle = sym_circle.relationships.add()
    rel_circle.symbol = "python test-project shapes/Shape#"
    rel_circle.is_implementation = True

    # Symbol: Circle.area() 方法（重写 Shape.area()）
    occ_circle_area_def = doc.occurrences.add()
    occ_circle_area_def.symbol = "python test-project shapes/Circle#area()."
    occ_circle_area_def.range.extend([35, 4, 45, 0])
    occ_circle_area_def.symbol_roles = scip_pb2.Definition

    sym_circle_area = doc.symbols.add()
    sym_circle_area.symbol = "python test-project shapes/Circle#area()."
    sym_circle_area.display_name = "area"
    sym_circle_area.kind = scip_pb2.SymbolInformation.Method
    sym_circle_area.documentation.extend(["Circle area: πr²"])

    # Symbol: Rectangle 类（实现 Shape）
    occ_rect_def = doc.occurrences.add()
    occ_rect_def.symbol = "python test-project shapes/Rectangle#"
    occ_rect_def.range.extend([55, 0, 75, 0])
    occ_rect_def.symbol_roles = scip_pb2.Definition

    sym_rect = doc.symbols.add()
    sym_rect.symbol = "python test-project shapes/Rectangle#"
    sym_rect.display_name = "Rectangle"
    sym_rect.kind = scip_pb2.SymbolInformation.Class
    sym_rect.documentation.extend(["Rectangle shape"])

    # Relationship: Rectangle 实现了 Shape
    rel_rect = sym_rect.relationships.add()
    rel_rect.symbol = "python test-project shapes/Shape#"
    rel_rect.is_implementation = True

    # Symbol: Rectangle.area() 方法（重写 Shape.area()）
    occ_rect_area_def = doc.occurrences.add()
    occ_rect_area_def.symbol = "python test-project shapes/Rectangle#area()."
    occ_rect_area_def.range.extend([60, 4, 70, 0])
    occ_rect_area_def.symbol_roles = scip_pb2.Definition

    sym_rect_area = doc.symbols.add()
    sym_rect_area.symbol = "python test-project shapes/Rectangle#area()."
    sym_rect_area.display_name = "area"
    sym_rect_area.kind = scip_pb2.SymbolInformation.Method
    sym_rect_area.documentation.extend(["Rectangle area: width * height"])

    # 保存
    with open("tests/fixtures/test_hierarchy.scip", "wb") as f:
        f.write(pb_index.SerializeToString())

    print("Created tests/fixtures/test_hierarchy.scip")


if __name__ == "__main__":
    create_test_hierarchy()

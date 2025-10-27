"""測試代碼分析節點功能"""

import json
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from lol_chat_helper.nodes import create_code_analyzer_node

import os
import dotenv
dotenv.load_dotenv()

# 模擬工具返回的大量表格數據
MOCK_ITEMS_DATA = {
    "column_descriptions": {
        "item_id": "物品ID",
        "name": "物品名稱",
        "description": "物品描述",
        "price": "價格"
    },
    "rows": [
        {"item_id": 1, "name": "多蘭之劍", "description": "提供攻擊力和生命值", "price": 450},
        {"item_id": 2, "name": "多蘭之盾", "description": "提供生命值和護甲", "price": 450},
        {"item_id": 3, "name": "黑魔禁書", "description": "提供法術強度和冷卻縮減", "price": 2800},
        {"item_id": 4, "name": "無盡之刃", "description": "大幅提升暴擊傷害", "price": 3400},
        {"item_id": 5, "name": "守護天使", "description": "死亡後可復活", "price": 3200},
        # 模擬更多數據...
    ] + [
        {"item_id": i, "name": f"測試物品{i}", "description": f"測試描述{i}", "price": 1000 + i*100}
        for i in range(6, 50)
    ]
}


def test_code_analyzer():
    """測試代碼分析節點"""
    print("=" * 60)
    print("測試代碼分析節點")
    print("=" * 60)
    
    # 初始化模型
    model = ChatOpenAI(
        base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
        api_key="lm-studio",
        model=os.getenv("MODEL_NAME", "qwen2.5-14b-instruct"),
        temperature=0.1,
    )
    
    # 創建代碼分析節點
    analyzer_node = create_code_analyzer_node(model)
    
    # 模擬消息流
    user_message = HumanMessage(content="我想要知道黑魔禁書的效果")
    
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "lol_list_items",
            "args": {"region": "kr"},
            "id": "call_123"
        }]
    )
    
    tool_message = ToolMessage(
        content=json.dumps(MOCK_ITEMS_DATA, ensure_ascii=False),
        tool_call_id="call_123",
        name="lol_list_items"
    )
    
    # 構建狀態
    state = {
        "messages": [user_message, ai_message, tool_message]
    }
    
    print("\n📊 原始數據大小:", len(json.dumps(MOCK_ITEMS_DATA)))
    print(f"   總共 {len(MOCK_ITEMS_DATA['rows'])} 個物品")
    
    # 執行代碼分析
    print("\n🔄 執行代碼分析...")
    result = analyzer_node(state)
    
    # 檢查結果
    if result["messages"]:
        new_messages = result["messages"]
        # 找到新的 ToolMessage
        for msg in new_messages:
            if isinstance(msg, ToolMessage):
                new_content = json.loads(msg.content)
                print(f"\n✅ 分析完成！")
                print(f"   篩選後的數據大小:", len(msg.content))
                print(f"   找到 {len(new_content)} 個匹配項目")
                print(f"\n📋 結果:")
                print(json.dumps(new_content, ensure_ascii=False, indent=2))
                break
    else:
        print("\n⚠️  沒有生成新的消息")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_code_analyzer()

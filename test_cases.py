# test_cases.py
"""
Тестовые случаи для проверки функциональности
"""

TEST_CASES = {
    "simple": "A->B,C;B->D,E;C->F;D->G;E->H;F->I",
    "cycle": "A->B;B->C;C->A",
    "multiple_cycles": "A->B,C;B->D,C;D->A;E->F;F->E",
    "deep_chain": "A->B;B->C;C->D;D->E;E->F;F->G;G->H;H->I;I->J",
    "complex": "A->B,C,D;B->E,F;C->B,G;D->H;E->I;F->J;G->K;H->L"
}

def create_test_files():
    """Создание тестовых файлов"""
    for name, content in TEST_CASES.items():
        filename = f"test_{name}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Создан: {filename}")

if __name__ == "__main__":
    create_test_files()

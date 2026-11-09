# Java 스택과 큐

## 스택은 LIFO, 큐는 FIFO

| 자료구조 | 꺼내는 순서 | a, b 순서로 넣었을 때 |
| --- | --- | --- |
| 스택 | LIFO(후입선출): 마지막에 넣은 값부터 | b, a |
| 큐 | FIFO(선입선출): 먼저 넣은 값부터 | a, b |

스택은 쌓아 놓은 접시처럼 마지막에 올린 것을 먼저 꺼낸다.
큐는 줄을 서듯 먼저 들어온 것부터 꺼낸다.
`Deque`는 양쪽 끝에서 삽입·제거할 수 있어 사용하는 메서드에 따라 스택이나 큐로 쓸 수 있다.

## Deque를 스택으로 사용하기

```java
import java.util.ArrayDeque;
import java.util.Deque;

// 메서드 내부에서 사용
Deque<Character> stack = new ArrayDeque<>();
stack.push('a');
stack.push('b');
char top = stack.peek();   // 'b': 원소는 그대로 남음
char first = stack.pop();  // 'b': 원소를 꺼내 제거
char second = stack.pop(); // 'a'
boolean empty = stack.isEmpty(); // true
```

제네릭에 `char` 대신 `Character`를 쓰는 이유와 자동 변환은
[타입과 문자열 변환](type-conversion.md#char와-character)을 참고한다.

| 메서드 | 동작 | 비어 있을 때 |
| --- | --- | --- |
| `push(value)` | 맨 위에 값 추가 | 값을 추가함 |
| `peek()` | 맨 위 값을 확인하며 제거하지 않음 | `null` 반환 |
| `pop()` | 맨 위 값을 제거하고 반환 | `NoSuchElementException` 발생 |
| `isEmpty()` | 비어 있으면 `true`, 아니면 `false` 반환 | `true` 반환 |

Java의 `Deque`에는 `top()` 메서드가 없으므로 맨 위를 확인할 때 `peek()`를 사용한다.
`isEmpty`는 필드가 아니라 메서드이므로 `stack.isEmpty()`처럼 괄호가 필요하다.

큐로 쓰려면 `offer()`로 뒤에 넣고 `poll()`로 앞에서 꺼낸다.

```java
Deque<Character> queue = new ArrayDeque<>();
queue.offer('a');
queue.offer('b');
char first = queue.poll();  // 'a'
char second = queue.poll(); // 'b'
```

## peek를 반복해도 다음 원소로 이동하지 않는다

스택을 바꾸지 않고 `peek()`를 두 번 호출하면 같은 원소를 두 번 읽는다.
첫 호출 결과를 `prev`에 저장한 뒤 다시 `peek()`와 비교해 같다고 해도,
서로 다른 두 원소가 같은 값이라는 뜻은 아니다.
이 상태에서 `pop()`을 두 번 호출하면 값이 다른 두 원소까지 제거할 수 있다.

## 스택에 값 대신 인덱스 저장하기

나중에 원래 위치의 결과를 갱신해야 한다면 `Deque<Integer>`에 배열의 인덱스를 저장한다.
스택에 무엇을 넣었는지에 따라 `peek()`와 `pop()`의 반환값을 해석해야 한다.

| 표현 | 인덱스를 저장한 스택에서의 의미 |
| --- | --- |
| `stack.peek()` | 맨 위에 저장된 인덱스 |
| `numbers[stack.peek()]` | 그 인덱스에 있는 원소 값 |
| `stack.pop()` | 맨 위 인덱스를 제거하고 반환 |
| `answer[index]` | 해당 위치에 기록할 결과 |

```java
int[] numbers = {4, 7};
int[] answer = new int[numbers.length];
Deque<Integer> stack = new ArrayDeque<>();
stack.push(0);

int index = stack.pop();
answer[index] = numbers[1]; // answer[0] = 7
```

`pop()`의 반환값을 사용하면 `peek()`로 위치를 읽고 별도로 `pop()`하는 동작을 합칠 수 있다.
숫자의 대소를 비교할 때는 `numbers[i]`와 `numbers[stack.peek()]`를 비교하고,
결과를 기록할 때는 스택에서 꺼낸 인덱스를 그대로 `answer`의 위치로 사용한다.
`answer[numbers[index]]`는 원소 값을 위치로 사용하므로 다른 칸을 수정하거나 범위를 벗어날 수 있다.

이 방식을 활용해 아직 답을 찾지 못한 인덱스를 관리하는 원리는
[단조 스택](../algorithms/monotonic-stack.md)에 정리되어 있다.

## 인접한 같은 값을 제거할 때의 스택 상태

문자를 왼쪽부터 읽으며 스택에 **지금까지 읽은 부분에서 짝을 제거하고 남은 문자**를 담는다.
스택의 맨 위는 현재 문자와 비교해야 할, 가장 최근에 남은 문자다.

- 맨 위와 현재 문자가 같으면 맨 위를 한 번 꺼낸다.
- 스택이 비었거나 맨 위와 다르면 현재 문자를 넣는다.

현재 문자는 아직 스택에 넣지 않았으므로 `pop()` 한 번과 현재 문자를 넣지 않는 동작으로
두 문자가 함께 제거된다. 두 번 꺼내면 그보다 앞에 남아 있던 문자까지 지우게 된다.
예를 들어 `"xyyx"`를 읽을 때 스택은 오른쪽을 맨 위로 표시하면
`[x] -> [x, y] -> [x] -> []`가 된다.
안쪽의 짝을 제거한 뒤 새로 인접하게 된 바깥쪽 문자도 자연스럽게 비교할 수 있다.

비교 전에는 빈 스택을 먼저 확인한다.

```java
// c는 현재 읽은 char 값
if (!stack.isEmpty() && stack.peek() == c) {
    stack.pop();
}
```

`&&`는 왼쪽이 거짓이면 오른쪽을 평가하지 않으므로 빈 스택의 `null`을 언박싱하지 않는다.
이 조건이 거짓일 때는 현재 문자를 스택에 넣는다.
전체 순회 후 스택이 비어 있으면 모든 문자가 짝으로 제거된 것이다.

각 문자는 최대 한 번 들어가고 한 번 나온다. `ArrayDeque`의 삽입은 분할 상환 `O(1)`이고
맨 위 조회·제거는 `O(1)`이므로 길이 n의 문자열 처리 시간은 `O(n)`이다.
아무 짝도 제거되지 않으면 n개의 문자가 남으므로 최악의 추가 공간은 `O(n)`이다.

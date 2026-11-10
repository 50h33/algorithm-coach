# Java 리스트와 배열 변환

반환 타입이 `int[]`이면 정수 기본형 배열을 만들어야 한다.
`List<Integer>`, `Integer[]`, `int[]`는 서로 다른 타입이다.

## 세 타입 구분하기

| 타입 | 특징 |
| --- | --- |
| `List<Integer>` | Integer 값을 저장하는 리스트. ArrayList는 원소를 추가하며 크기를 늘릴 수 있음 |
| `Integer[]` | Integer 객체를 담는 고정 길이 배열. 원소로 null을 가질 수 있음 |
| `int[]` | int 기본형을 담는 고정 길이 배열. 새 배열의 원소는 0으로 초기화 |

Map과 List의 제네릭에 Integer를 쓰는 이유는 [타입과 문자열 변환](type-conversion.md)에 정리되어 있다.

## 배열 길이와 인덱스 범위

```java
int[] empty = {};       // 길이 0: empty[0]도 접근 불가
int[] numbers = new int[4]; // 길이 4: {0, 0, 0, 0}

for (int i = 0; i < numbers.length; i++) {
    numbers[i] = i;
}
```

길이가 N인 배열의 유효한 인덱스는 0부터 N - 1까지다. 반복 조건을 `i <= numbers.length`로
쓰면 마지막에 인덱스 N에 접근하므로 `ArrayIndexOutOfBoundsException`이 발생한다.
`Index 4 out of bounds for length 4`는 길이 4인 배열의 인덱스 4에 접근했다는 뜻이다.
`Index 0 out of bounds for length 0`은 빈 배열의 첫 칸에 접근했다는 뜻이다.

배열은 원소를 대입하거나 증가시켜도 길이가 늘어나지 않는다. 결과가 사용자마다 하나씩 필요하면
사용자 수만큼 배열을 생성하는 등, 저장할 결과 개수에 맞춰 길이를 지정한다.

## 길이, 인덱스, 원소 값 구분

배열의 **길이**, **인덱스**, **원소 값**은 서로 다른 정보다.

```java
int[] values = {4, 8, 9};
int length = values.length; // 3: 원소 개수
int index = 1;              // 1: 두 번째 원소의 위치
int value = values[index];  // 8: 해당 위치에 저장된 값
```

찾아낸 원소의 값을 결과에 담으려면 `values[index]`를 사용한다.
`values.length`를 담으면 찾은 값과 관계없이 배열 길이만 저장된다.
원소 값을 다시 인덱스로 사용하면 엉뚱한 위치를 가리키거나 배열 범위를 벗어날 수 있다.

## length, length(), size() 구분

| 대상 | 크기 확인 | 형태 |
| --- | --- | --- |
| 배열 | `array.length` | 필드: 괄호 없음 |
| String | `text.length()` | 메서드 |
| List, Set, Map | `collection.size()` | 메서드 |

배열에 `length()`를 호출하면 해당 메서드가 없으므로 `cannot find symbol` 컴파일 오류가 난다.
배열의 원소가 문자열이어도 배열 자체의 길이는 `length`로 확인한다.

```java
String[][] groups = {{"abc", "de"}, {"f"}};
int groupCount = groups.length;       // 2: 바깥 배열 길이
int itemCount = groups[0].length;     // 2: 첫 번째 내부 배열 길이
int textLength = groups[0][0].length(); // 3: 문자열 길이
int[] result = new int[groups.length]; // 그룹마다 결과 하나
```

내부 배열의 길이는 서로 다를 수 있다. `groups[0]`이나 `groups[0][0]`에 접근하려면
해당 원소가 존재하고 null이 아니어야 한다.

## Arrays.fill로 배열 초기화하기

`new int[n]`의 원소는 기본적으로 0이다. 다른 값으로 채우려면 `Arrays.fill`을 사용한다.
이 메서드는 기존 배열의 내용을 바꾼다. `import java.util.Arrays;` 또는 `import java.util.*;`가 필요하다.

```java
int[] values = new int[3];
Arrays.fill(values, -1); // {-1, -1, -1}

int[][] dist = new int[2][3];
for (int[] row : dist) {
    Arrays.fill(row, -1);
}
dist[0][0] = 0; // 출발점만 거리 0
```

2차원 배열은 행 배열들의 배열이므로 각 행에 `fill`을 적용한다.
`Arrays.fill(dist, -1)`로 모든 정수 칸을 채울 수는 없다.
향상된 for문에서 `row`는 실제 행 배열을 가리키므로 행을 채우면 `dist`에도 반영된다.
행 수가 n, 열 수가 m인 배열 전체를 채우는 시간은 `O(nm)`이다.
거리 배열을 방문 표시로 함께 사용하는 방법은 [거리 제한 BFS](../algorithms/bfs.md)에 정리되어 있다.

## toArray는 int[]를 만들지 않는다

```java
// import java.util.*;

List<Integer> values = new ArrayList<>();
values.add(10);
values.add(20);

Integer[] boxed = values.toArray(new Integer[0]); // {10, 20}
// int[] numbers = values.toArray(new Integer[0]); // 타입 불일치
```

`toArray(new Integer[0])`는 Integer[] 타입을 지정한다.
리스트에 원소가 있으면 필요한 길이의 배열을 만들어 반환하므로 결과가 길이 0인 배열이라는 뜻은 아니다.

Integer 값 하나를 int로 언박싱할 수 있어도 Integer[] 전체가 int[]로 자동 변환되지는 않는다.
`values.toArray(new int[0])`도 컴파일 오류다. 이 메서드의 제네릭 `T[]`에는
`Integer[]` 같은 참조형 원소의 배열이 필요하며, `int[]`를 전달할 수 없다.

## 이미 있는 리스트를 int[]로 변환하기

### Stream 사용

```java
// values는 위 예제의 List<Integer>
int[] numbers = values.stream()
        .mapToInt(Integer::intValue)
        .toArray();
// {10, 20}
```

처리 순서는 다음과 같다.

1. `stream()`: 리스트 원소를 `Stream<Integer>`로 읽는다.
2. `mapToInt(Integer::intValue)`: 각 Integer에서 int 값을 꺼내 IntStream으로 바꾼다.
3. `toArray()`: IntStream의 값으로 int[]를 만든다.

`Integer::intValue`는 `value -> value.intValue()`와 같은 역할을 한다.
`mapToInt(value -> value)`로 써도 반환하는 Integer가 int로 자동 언박싱된다.
리스트에 null이 있으면 값을 꺼내는 과정에서 예외가 발생한다.

### 반복문 사용

Stream 없이 원소를 하나씩 배열에 복사할 수도 있다.

```java
int[] numbers = new int[values.size()];
int index = 0;

for (int value : values) {
    numbers[index++] = value;
}
```

이 경우에도 원소가 null이면 언박싱할 수 없다.

## 결과 개수를 알면 배열에 바로 저장하기

반환할 값의 개수를 미리 알면 중간 List 없이 int[]를 만들 수 있다.
다음 예제는 Map의 값마다 하나의 결과를 만드는 경우다.

```java
// import java.util.*;

Map<String, Integer> totals = new TreeMap<>();
totals.put("banana", 20);
totals.put("apple", 10);

int[] answer = new int[totals.size()];
int index = 0;

for (int total : totals.values()) {
    answer[index++] = total;
}
// answer = {10, 20}
```

`answer[index++]`는 현재 index 위치에 저장한 뒤 index를 1 증가시킨다.
반환 타입이 int[]인 메서드에서는 채운 배열을 `return answer;`로 반환하면 된다.

Map 항목당 결과가 하나일 때만 Map의 size를 그대로 결과 길이로 쓸 수 있다.
필터링으로 일부 항목을 제외한다면 실제 결과 개수에 맞춰 크기를 정해야 한다.
배열을 채우는 순서는 원본 자료구조의 순회 순서이므로, 출력 순서가 중요하면
[Map 정렬 방식](map.md)도 확인한다.

| 상황 | 선택 |
| --- | --- |
| 결과 개수를 미리 알고 int[]가 필요함 | 처음부터 int[] 생성 |
| 결과 개수가 가변적임 | `ArrayList<Integer>`에 모은 뒤 변환 |
| 이미 `List<Integer>`가 있음 | Stream 또는 반복문으로 int[] 변환 |
| Integer[] 자체가 필요함 | toArray(new Integer[0]) |

## 결과의 최대 개수만 알 때: Arrays.copyOf

필터링 결과의 정확한 개수를 몰라도 최대 개수를 알면 배열에 직접 저장할 수 있다.
배열의 길이와 실제 저장한 개수를 따로 관리한다.

```java
// import java.util.Arrays;
int[] values = {1, 2, 3, 4};
int[] answer = new int[values.length];
int count = 0;

for (int value : values) {
    if (value % 2 == 1) {
        answer[count] = value;
        count++;
    }
}
// answer는 {1, 3, 0, 0}, count는 2
int[] result = Arrays.copyOf(answer, count); // {1, 3}
```

`Arrays.copyOf(answer, count)`는 앞에서 count개를 복사한 새 배열을 반환한다.
원본 배열의 길이는 바뀌지 않는다. count가 0이면 빈 배열이 된다.
값이 0인 원소를 제거하는 기능이 아니므로, 결과에 실제 0이 있어도 보존된다.
이 방식은 `0 <= count <= answer.length`를 유지하며, 복사에 `O(count)` 시간과 공간이 든다.

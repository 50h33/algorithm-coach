# Java Map 조회와 누적 및 정렬

Map은 키 하나에 값 하나를 연결하는 자료구조다. 키별 개수나 누적값을 저장할 때 사용할 수 있다.
다음 예제는 파일 상단에 `import java.util.*;`를 선언한 뒤 메서드 안에서 사용하는 코드 조각이다.

## 선언과 기본 메서드

```java
Map<String, Integer> map = new HashMap<>();
map.put("apple", 10);
map.put("banana", 20);
```

`Map<String, Integer>`는 키가 문자열이고 값이 정수 객체인 Map이다.
제네릭에는 `int` 대신 `Integer`를 쓴다. 자세한 내용은 [타입과 문자열 변환](type-conversion.md)을 참고한다.

| 목적 | 코드 | 동작 |
| --- | --- | --- |
| 저장·변경 | `map.put(key, value)` | 같은 키가 있으면 기존 값을 덮어씀 |
| 조회 | `map.get(key)` | 키에 연결된 값 반환. 키가 없으면 null |
| 기본값을 지정한 조회 | `map.getOrDefault(key, 0)` | 키가 없으면 0 반환 |
| 키 존재 확인 | `map.containsKey(key)` | 키가 있으면 true |
| 삭제 | `map.remove(key)` | 키와 연결된 값을 제거 |
| 항목 개수 | `map.size()` | 키·값 쌍의 개수 |

`getOrDefault()`는 조회만 하며 기본값을 Map에 저장하지 않는다.
키가 있지만 값이 `null`인 경우에는 기본값 대신 `null`을 반환한다.

```java
int apple = map.get("apple");              // 10
int orange = map.getOrDefault("orange", 0); // 0
boolean exists = map.containsKey("orange"); // false

map.put("empty", null);
Integer empty = map.getOrDefault("empty", 0); // null
```

`int value = map.get("없는 키");`처럼 `null`을 `int`로 받으면 언박싱 과정에서
`NullPointerException`이 발생한다. 값으로 null을 저장할 수 있는 경우에는 별도 처리가 필요하다.

## 같은 키에 값 누적하기

### merge

```java
Map<String, Integer> counts = new HashMap<>();

counts.merge("apple", 1, Integer::sum); // 1
counts.merge("apple", 1, Integer::sum); // 2
counts.merge("apple", 3, Integer::sum); // 5
```

`merge(key, 추가할값, 합치는함수)`는 키가 없거나 기존 값이 null이면 전달한 값을 저장한다.
기존 값이 null이 아니면 합치는 함수에 기존 값과 전달한 값을 넣어 결과를 저장한다.
여기에 전달하는 추가 값은 null이면 안 된다.

이 예제의 `Integer::sum`은 두 정수를 더하는 함수다.
`(oldValue, addedValue) -> oldValue + addedValue`로 써도 같은 역할을 한다.

### getOrDefault와 put

```java
Map<String, Integer> counts = new HashMap<>();

counts.put("apple", counts.getOrDefault("apple", 0) + 1); // 1
counts.put("apple", counts.getOrDefault("apple", 0) + 1); // 2
```

현재 값을 읽고 없으면 0을 사용한 뒤, 증가시킨 값을 다시 저장한다.
null 값을 저장하지 않는 Map에서는 두 방식 모두 빈도수를 누적하는 데 사용할 수 있다.
기존 값이 null이면 이 방식의 `+ 1`에서 예외가 발생하므로 merge와 null 처리가 같지는 않다.

## 필요한 항목 순회하기

```java
Map<String, Integer> map = new HashMap<>();
map.put("apple", 10);
map.put("banana", 20);

// 값만 필요할 때
for (int value : map.values()) {
    System.out.println(value);
}

// 키만 필요할 때
for (String key : map.keySet()) {
    System.out.println(key);
}

// 키와 값이 모두 필요할 때
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    int value = entry.getValue();
    System.out.println(key + ": " + value);
}
```

`Map.Entry`는 키·값 한 쌍이다. 이 예제처럼 값에 null이 없을 때는 `int`로 받아 사용할 수 있다.
순회에 필요한 정보에 맞춰 `values()`, `keySet()`, `entrySet()`을 고른다.
HashMap 예제의 출력 순서는 정해져 있지 않다.

## 키 순서대로 순회하기

| 구현체 | 순회 순서 |
| --- | --- |
| HashMap | 순서 보장 없음 |
| TreeMap | 키의 자연 순서 또는 생성할 때 지정한 Comparator 순서 |
| LinkedHashMap | 기본 생성 방식에서는 삽입 순서 |

정수 키의 기본 TreeMap은 작은 키부터 순회한다. 값의 크기로 정렬하는 것이 아니다.

```java
Map<Integer, Integer> map = new TreeMap<>();
map.put(3, 100);
map.put(1, 200);
map.put(2, 300);

for (Map.Entry<Integer, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + " " + entry.getValue());
}
```

출력:

```text
1 200
2 300
3 100
```

기존 HashMap의 내용을 정렬된 새 Map으로 복사할 수도 있다.

```java
Map<Integer, Integer> original = new HashMap<>();
original.put(3, 100);
original.put(1, 200);

Map<Integer, Integer> sorted = new TreeMap<>(original);
```

원래 Map 자체가 바뀌는 것은 아니다. TreeMap의 조회·삽입·삭제는 각각 `O(log N)`이다.

문자열 키는 기본적으로 사전순이다. `"10"`은 `"2"`보다 먼저 온다.
반면 `"0002"`, `"0010"`처럼 길이가 같고 0으로 자릿수를 맞춘 숫자 문자열은
사전순과 숫자 크기 순서가 일치한다.

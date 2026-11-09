# Java Set 선언과 중복 처리

Set은 중복 없는 원소를 저장하는 집합이다. `Map<K, V>`와 달리 원소 타입 하나만 지정한다.
아래 예제는 `import java.util.*;`를 선언하고 메서드 안에서 사용한다.

## 선언과 기본 메서드

```java
Set<String> names = new HashSet<>();

names.add("ryan");      // 처음 추가: true
names.add("ryan");      // 이미 존재: false, 원소는 하나만 유지
names.contains("ryan"); // true
names.contains("con");  // false
names.size();           // 1
```

`Set<String>`은 문자열 집합 타입이고 `HashSet`은 그 구현체다.
`Set<String, String>`처럼 타입을 두 개 지정할 수 없다.
HashSet은 순회 순서를 보장하지 않는다. 문자열은 내용이 같으면 같은 원소로 취급한다.

Set에는 키와 값의 구분이 없으므로 원소 존재 여부는 `contains(value)`로 확인한다.
Map의 키 존재 여부를 확인하는 `containsKey(key)`와 구분한다.
Map 안에 Set을 저장하는 방법은 [Map의 컬렉션 값](map.md#값으로-list나-set-저장하기)을 참고한다.

## 중복 확인과 추가 결과 활용하기

중복 원소를 건너뛰려면 `contains()`로 확인한 뒤 추가할 수 있다.

```java
String[] input = {"apple", "apple", "banana"};
Set<String> seen = new HashSet<>();

for (String value : input) {
    if (seen.contains(value)) continue;
    seen.add(value);
    System.out.println(value);
}
// apple과 banana를 각각 한 번 출력
```

`add()`가 새 원소를 추가했는지 반환한다는 점을 이용해 같은 처리를 표현할 수도 있다.

```java
Set<String> seen = new HashSet<>();
int count = 0;

for (String value : input) {
    if (seen.add(value)) {
        count++;
    }
}
// count는 2
```

List를 Set으로 바꾸더라도 별도의 카운터나 Map에서 매번 증가시키면 중복 집계는 남는다.
고유 원소를 세는 경우에는 새로운 원소가 추가됐을 때만 증가시킨다.
중복 여부는 목적에 맞는 단위로 판단한다. 서로 다른 두 사람의 관계를 구별해야 한다면
한 사람 이름만으로 중복을 판단하지 않고, 두 사람의 조합을 구별해야 한다.

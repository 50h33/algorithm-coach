# Java 타입과 문자열 변환

기본형과 객체형을 구분하고, 입력 문자열을 계산에 사용할 숫자로 바꾸는 방법을 정리한다.

## int와 Integer

`int`는 정수 기본형이고 `Integer`는 정수를 감싸는 래퍼 클래스다.
Map이나 List의 제네릭 타입 인자에는 기본형을 넣을 수 없으므로 `Integer`를 쓴다.

```java
// import java.util.*;

// Map<String, int> map = new HashMap<>(); // 컴파일 오류
Map<String, Integer> map = new HashMap<>();
List<Integer> values = new ArrayList<>();
```

`Map.Entry<String, Integer>`의 값 타입도 같은 방식으로 지정한다.

```java
Integer boxed = 10; // int -> Integer: 오토박싱
int number = boxed; // Integer -> int: 언박싱
```

Integer에는 null을 저장할 수 있지만 int에는 저장할 수 없다.
null인 Integer를 int로 바꾸려 하면 `NullPointerException`이 발생한다.

```java
Integer missing = null;
// int number = missing; // 실행 시 NullPointerException
```

## 문자열과 숫자 변환

| 변환 | 코드 | 결과 |
| --- | --- | --- |
| String → int | `Integer.parseInt("123")` | 123 |
| String → long | `Long.parseLong("3000000000")` | 3000000000L |
| int → String | `String.valueOf(123)` | "123" |

```java
String text = "123";
int number = Integer.parseInt(text);
String converted = String.valueOf(number);
```

parseInt는 숫자로 해석할 수 없는 문자열이나 int 범위를 벗어나는 문자열에서
`NumberFormatException`을 발생시킨다. 예를 들어 `"abc"`, `"3.2"`는 int로 파싱할 수 없다.
큰 정수가 필요하면 입력 범위에 맞춰 long과 `Long.parseLong()`을 사용한다.

## 숫자 문자 하나 변환하기

```java
char digit = '7';
int number = digit - '0'; // 7

int value = 7;
char restored = (char) (value + '0'); // '7'
```

`digit - '0'`은 digit이 `'0'`부터 `'9'`까지의 문자일 때 사용한다.
반대로 `(char) (value + '0')`는 value가 0부터 9일 때 숫자 문자 하나를 만든다.

`'7'`은 char이고 `"7"`은 String이다.
문자열 전체를 숫자로 바꿀 때는 문자 뺄셈 대신 parseInt를 사용한다.

## 구분자로 나눈 시간 문자열을 분으로 변환하기

시간과 분을 하나의 단위로 바꾸면 시간 차이를 뺄셈으로 계산할 수 있다.
유효한 24시간제 `HH:mm` 형식의 문자열을 전제로 한다.

```java
String time = "09:35";
String[] parts = time.split(":");

int hour = Integer.parseInt(parts[0]);   // 9
int minute = Integer.parseInt(parts[1]); // 35
int totalMinutes = hour * 60 + minute;   // 575
```

예를 들어 같은 날 09:35부터 10:05까지의 시간 차이는
`(10 * 60 + 5) - 575 = 30`분이다. 날짜가 넘어가는 시간은 날짜 정보도 고려해야 한다.

관련 노트: [Map 조회와 누적](map.md), [리스트와 배열 변환](list-and-array.md).

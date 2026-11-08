# Java 문자열 접근과 문자 비교

## 인덱스로 문자 가져오기: charAt

`String`은 배열이 아니므로 `s[i]`로 접근할 수 없다. `s.charAt(i)`로 해당 위치의 `char` 값을 가져온다.
인덱스는 0부터 시작하며, 유효한 범위는 `0`부터 `s.length() - 1`까지다.

```java
String s = "cabca";
char first = s.charAt(0); // 'c'
char next = s.charAt(1);  // 'a'

char[] letters = {'c', 'a'};
char value = letters[1]; // 배열에는 [] 사용: 'a'
```

빈 문자열에는 유효한 문자 인덱스가 없다. 범위를 벗어난 `charAt` 호출은 예외를 발생시킨다.
`array required, but String found`는 배열 접근 문법을 String에 사용했다는 뜻이다.

## 문자나 문자열의 위치 찾기: indexOf

`charAt`은 인덱스로 문자를 가져오고, `indexOf`는 찾을 값이 처음 등장하는 위치를 반환한다.
`indexOf`의 결과는 `int`이며, 찾지 못하면 `-1`이다.

```java
String s = "cabca";
char letter = s.charAt(1);       // 'a'
int firstIndex = s.indexOf('a'); // 1: 마지막의 'a'가 아닌 첫 번째 위치
int wordIndex = s.indexOf("bc"); // 2
int missing = s.indexOf('z');    // -1
```

이미 인덱스를 가지고 있고 그 위치의 문자가 필요하다면 `charAt`을 사용한다.

## char는 ==, String 내용은 equals

`char`는 기본형이므로 메서드를 호출할 수 없다. 문자 값의 같고 다름은 `==`, `!=`로 비교한다.

```java
String s = "cabca";
char first = s.charAt(0);
boolean same = first == s.charAt(3);      // true
boolean different = first != s.charAt(1); // true
// first.equals(s.charAt(3)); // 컴파일 오류: char cannot be dereferenced
```

`String`의 내용 비교에는 `.equals()`를 사용한다. String에 대한 `==`는 같은 객체를 가리키는지 비교한다.

```java
String left = new String("cat");
String right = new String("cat");
boolean sameText = left.equals(right); // true
boolean sameObject = left == right;   // false
```

숫자 문자와 숫자 사이의 변환은 [타입과 문자열 변환](type-conversion.md)에 정리되어 있다.

# Java 정수 나눗셈과 올림

나눗셈은 피연산자의 타입에 따라 결과가 달라진다.
형변환을 어느 시점에 하는지와 올림 함수의 반환 타입을 함께 확인해야 한다.

## int끼리 나누면 소수 부분이 사라진다

```java
int a = 7;
int b = 3;

int quotient = a / b;          // 2
double alreadyDivided = a / b; // 2.0
double fractional = (double) a / b; // 약 2.3333
```

결과를 double 변수에 저장하더라도, `a / b`를 먼저 int 연산으로 계산하면 소수 부분은 이미 사라진다.
소수 결과가 필요하면 나누기 전에 적어도 한쪽을 double로 바꾼다.
정수 나눗셈은 0을 향해 소수 부분을 버리므로 `-7 / 3`은 -2이며, 수학적인 내림과는 다르다.

## ceil과 floor 및 round

| 함수 | 동작 | 예시 | 반환 타입 |
| --- | --- | --- | --- |
| Math.ceil(double) | 입력값 이상인 가장 작은 정수값 | ceil(3.2) → 4.0 | double |
| Math.floor(double) | 입력값 이하인 가장 큰 정수값 | floor(3.8) → 3.0 | double |
| Math.round(double) | 가장 가까운 정수, 동률이면 양의 방향 | round(3.5) → 4 | long |
| Math.round(float) | 가장 가까운 정수, 동률이면 양의 방향 | round(3.5f) → 4 | int |

음수에서도 같은 정의를 적용한다. `ceil(-3.2)`는 -3.0, `floor(-3.2)`는 -4.0,
`round(-3.5)`는 -3이다.

```java
double roundedUp = Math.ceil(3.2); // 4.0
int integerResult = (int) Math.ceil(3.2); // 4
long rounded = Math.round(3.5); // 4
```

ceil의 결과가 정수값 모양이더라도 타입은 double이다.
int로 저장하려면 명시적 형변환이 필요하며, 값이 int 범위에 들어가는지도 확인한다.

## 나눗셈 결과를 올리는 순서

```java
int a = 7;
int b = 3;

int wrong = (int) Math.ceil(a / b);          // 2
int correct = (int) Math.ceil((double) a / b); // 3
```

첫 식은 정수 나눗셈 결과인 2를 ceil에 전달한다.
두 번째 식은 a를 먼저 double로 바꿔 약 2.3333을 전달하므로 3으로 올림된다.

`Math.ceil((double) (a / b))`도 늦은 형변환이다. 괄호 안의 정수 나눗셈이 먼저 수행된다.

## 정수 연산만으로 올림하기

a가 0 이상, b가 양수인 정수이면 다음 식으로 몫을 올릴 수 있다.

```java
int a = 7;
int b = 3;

int units = (a + b - 1) / b; // 3
```

나누어떨어지면 몫이 그대로이고, 나머지가 있으면 한 단위가 추가된다.
`6 / 3`은 2단위, `7 / 3`은 올림하여 3단위다.

이 식을 음수에 그대로 적용하면 안 된다. 또한 a와 b가 각각 int 범위 안이어도
`a + b - 1` 중간 계산은 오버플로할 수 있다. int 입력을 넓은 타입에서 더하려면
덧셈 전에 long으로 변환한다.

```java
long units = ((long) a + b - 1) / b; // a, b는 int, a >= 0, b > 0
```

## 기준값 이하인 경우를 분리하기

기본 사용량까지는 기본 비용만 적용하고 초과분에만 단위 비용을 부과한다면,
초과 계산을 기준값보다 클 때만 수행한다.

```java
int usage = 190;
int included = 180;
int step = 15;
int baseCost = 5000;
int stepCost = 1000;

int cost = baseCost;
if (usage > included) {
    int extra = usage - included;
    int units = (int) Math.ceil((double) extra / step);
    cost += units * stepCost;
}
// cost = 6000
```

사용량이 included 이하이면 추가 계산을 하지 않으므로 기본 비용을 유지한다.
기준 이하의 음수 차이를 초과분 계산식에 그대로 넣어 비용이 줄어들게 만들지 않는다.
일반적인 입력에서는 step이 양수인지와 곱셈·누적 결과의 범위도 확인한다.

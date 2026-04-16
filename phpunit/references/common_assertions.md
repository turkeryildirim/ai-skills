# Common PHPUnit Assertions

## Equality and Identity
- `assertSame($expected, $actual)`: Checks for same value and type (===).
- `assertEquals($expected, $actual)`: Checks for equality (==).
- `assertNotSame($expected, $actual)`
- `assertNotEquals($expected, $actual)`

## Types
- `assertInstanceOf($expected, $actual)`
- `assertIsArray($actual)`
- `assertIsBool($actual)`
- `assertIsFloat($actual)`
- `assertIsInt($actual)`
- `assertIsNumeric($actual)`
- `assertIsObject($actual)`
- `assertIsString($actual)`
- `assertIsNull($actual)`

## Strings
- `assertStringContainsString($needle, $haystack)`
- `assertStringStartsWith($prefix, $string)`
- `assertStringEndsWith($suffix, $string)`
- `assertMatchesRegularExpression($pattern, $string)`

## Arrays
- `assertArrayHasKey($key, $array)`
- `assertContains($needle, $haystack)`: Checks if value exists in array.
- `assertCount($expectedCount, $haystack)`

## Boolean
- `assertTrue($actual)`
- `assertFalse($actual)`

## Exceptions
- `$this->expectException(Exception::class)`
- `$this->expectExceptionMessage('Expected message')`
- `$this->expectExceptionCode(123)`

## File System
- `assertFileExists($path)`
- `assertDirectoryExists($path)`

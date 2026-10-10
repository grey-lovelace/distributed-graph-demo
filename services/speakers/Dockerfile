FROM gradle:8.14.6-jdk21 AS build
WORKDIR /build
COPY settings.gradle.kts build.gradle.kts ./
COPY src src
# The cache mount keeps downloaded dependencies between builds,
# so a code change does not download them again.
RUN --mount=type=cache,target=/home/gradle/.gradle gradle bootJar --no-daemon --quiet

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /build/build/libs/speakers.jar speakers.jar
EXPOSE 4001
CMD ["java", "-jar", "speakers.jar"]

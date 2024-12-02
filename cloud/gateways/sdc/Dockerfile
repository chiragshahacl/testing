FROM maven:3.9.8-amazoncorretto-21 AS build


COPY gateways/sdc/src/. /home/app/gateways/sdc/src/.
COPY gateways/sdc/pom.xml /home/app/gateways/sdc/.
RUN mvn -f /home/app/gateways/sdc/pom.xml clean package

FROM amazoncorretto:21.0.4
COPY --from=build /home/app/gateways/sdc/target/classes/Consumer-1.0.0-SNAPSHOT.jar  /usr/local/lib/sdc.jar

USER $USERNAME

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

ENTRYPOINT ["java","-jar","/usr/local/lib/sdc.jar"]
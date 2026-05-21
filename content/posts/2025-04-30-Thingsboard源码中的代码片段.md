---
title: "ThingsBoard 源码阅读笔记：关键代码片段整理"
date: 2025-04-30 08:00:00+08:00
slug: codes-in-thingsboard
categories: [ "tech" ]
tags: [ "thingsboard" ]
description: "记录 ThingsBoard 源码阅读过程中遇到的一些关键代码片段与实现细节，作为后续分析和查阅的笔记整理。"
---

Uuids

```bash
UUID uuid = Uuids.timeBased();
Uuids.unixTimestamp(uuid)

UUID NULL_UUID = Uuids.startOf(0);
```

<!--more-->

UUIDConverter

```java
public class UUIDConverter {

    public static UUID fromString(String src) {
        return UUID.fromString(src.substring(7, 15) + "-" + src.substring(3, 7) + "-1"
                + src.substring(0, 3) + "-" + src.substring(15, 19) + "-" + src.substring(19));
    }

    public static String fromTimeUUID(UUID src) {
        if (src.version() != 1) {
            throw new IllegalArgumentException("Only Time-Based UUID (Version 1) is supported!");
        }
        String str = src.toString();
        / 58e0a7d7-eebc-11d8-9669-0800200c9a66 => 1d8eebc58e0a7d796690800200c9a66. Note that [11d8] -> [1d8]
        return str.substring(15, 18) + str.substring(9, 13) + str.substring(0, 8) + str.substring(19, 23) + str.substring(24);
    }

    public static List<String> fromTimeUUIDs(List<UUID> uuids) {
        if (uuids == null) {
            return null;
        }
        return uuids.stream().map(UUIDConverter::fromTimeUUID).collect(Collectors.toList());
    }

}
```

TaskScheduler

```java
@Configuration
@EnableScheduling
public class SchedulingConfiguration implements SchedulingConfigurer {

    @Override
    public void configureTasks(ScheduledTaskRegistrar taskRegistrar) {
        taskRegistrar.setScheduler(taskScheduler());
    }

    @Bean(destroyMethod="shutdown")
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler threadPoolScheduler = new ThreadPoolTaskScheduler();
        threadPoolScheduler.setThreadNamePrefix("TB-Scheduling-");
        threadPoolScheduler.setPoolSize(Runtime.getRuntime().availableProcessors());
        threadPoolScheduler.setRemoveOnCancelPolicy(true);
        return threadPoolScheduler;
    }
}
```

MessageConfiguration

```java
@Configuration
public class ThingsboardMessageConfiguration {

    @Bean
    @Primary
    public MessageSource messageSource() {
        ResourceBundleMessageSource messageSource = new ResourceBundleMessageSource();
        messageSource.setBasename("i18n/messages");
        messageSource.setDefaultEncoding("UTF-8");
        return messageSource;
    }
}
```

redirect

```java
@Controller
public class WebConfig {

    @RequestMapping(value = {"/assets", "/assets/", "/{path:^(?!api$)(?!assets$)(?!static$)(?!webjars$)(?!swagger-ui$)[^\\.]*}/**"})
    public String redirect() {
        return "forward://index.html";
    }

    @RequestMapping("/swagger-ui.html")
    public void redirectSwagger(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String baseUrl = MiscUtils.constructBaseUrl(request);
        response.sendRedirect(baseUrl + "/swagger-ui/");
    }

    @RequestMapping("/swagger-ui/")
    public String redirectSwaggerIndex() throws IOException {
        return "forward://swagger-ui/index.html";
    }
}
```

WebSocketConfiguration

```java
@Configuration
@TbCoreComponent
@EnableWebSocket
@RequiredArgsConstructor
@Slf4j
public class WebSocketConfiguration implements WebSocketConfigurer {

    public static final String WS_API_ENDPOINT = "/api/ws";
    public static final String WS_PLUGINS_ENDPOINT = "/api/ws/plugins/";
    private static final String WS_API_MAPPING = "/api/ws/**";

    private final WebSocketHandler wsHandler;

    @Bean
    public ServletServerContainerFactoryBean createWebSocketContainer() {
        ServletServerContainerFactoryBean container = new ServletServerContainerFactoryBean();
        container.setMaxTextMessageBufferSize(32768);
        container.setMaxBinaryMessageBufferSize(32768);
        return container;
    }

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        if (!(wsHandler instanceof TbWebSocketHandler)) {
            log.error("TbWebSocketHandler expected but [{}] provided", wsHandler);
            throw new RuntimeException("TbWebSocketHandler expected but " + wsHandler + " provided");
        }
        registry.addHandler(wsHandler, WS_API_MAPPING).setAllowedOriginPatterns("*");
    }

}
```

CsvUtils

```java
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class CsvUtils {
    public static List<List<String>> parseCsv(String content, Character delimiter) throws Exception {
        CSVFormat csvFormat = delimiter.equals(",") ? CSVFormat.DEFAULT : CSVFormat.DEFAULT.withDelimiter(delimiter);

        List<CSVRecord> records;
        try (CharSequenceReader reader = new CharSequenceReader(content)) {
            records = csvFormat.parse(reader).getRecords();
        }

        return records.stream()
                .map(record -> Stream.iterate(0, i -> i < record.size(), i -> i + 1)
                        .map(record::get)
                        .collect(Collectors.toList()))
                .collect(Collectors.toList());
    }
}

```

MiscUtils

```java
public class MiscUtils {

    public static final Charset UTF8 = Charset.forName("UTF-8");

    public static String constructBaseUrl(HttpServletRequest request) {
        return String.format("%s://%s:%d",
                getScheme(request),
                getDomainName(request),
                getPort(request));
    }

    public static String getScheme(HttpServletRequest request){
        String scheme = request.getScheme();
        String forwardedProto = request.getHeader("x-forwarded-proto");
        if (forwardedProto != null) {
            scheme = forwardedProto;
        }
        return scheme;
    }

    public static String getDomainName(HttpServletRequest request){
        return request.getServerName();
    }

    public static String getDomainNameAndPort(HttpServletRequest request){
        String domainName = getDomainName(request);
        String scheme = getScheme(request);
        int port = MiscUtils.getPort(request);
        if (needsPort(scheme, port)) {
            domainName += ":" + port;
        }
        return domainName;
    }

    private static boolean needsPort(String scheme, int port) {
        boolean isHttpDefault = "http".equals(scheme.toLowerCase()) && port == 80;
        boolean isHttpsDefault = "https".equals(scheme.toLowerCase()) && port == 443;
        return !isHttpDefault && !isHttpsDefault;
    }

    public static int getPort(HttpServletRequest request){
        String forwardedProto = request.getHeader("x-forwarded-proto");

        int serverPort = request.getServerPort();
        if (request.getHeader("x-forwarded-port") != null) {
            try {
                serverPort = request.getIntHeader("x-forwarded-port");
            } catch (NumberFormatException e) {
            }
        } else if (forwardedProto != null) {
            switch (forwardedProto) {
                case "http":
                    serverPort = 80;
                    break;
                case "https":
                    serverPort = 443;
                    break;
            }
        }
        return serverPort;
    }
}
```

ThingsboardServerApplication：打印启动时间

```java
public class ThingsboardServerApplication {
    private static long startTs;

    public static void main(String[] args) {
        startTs = System.currentTimeMillis();
        SpringApplication.run(ThingsboardServerApplication.class, updateArguments(args));
    }

    @AfterStartUp(order = Ordered.LOWEST_PRECEDENCE)
    public void afterStartUp() {
        long startupTimeMs = System.currentTimeMillis() - startTs;
        log.info("Started ThingsBoard in {} seconds", TimeUnit.MILLISECONDS.toSeconds(startupTimeMs));
    }

}
```

TemplateUtils

```java
public class TemplateUtils {

    private static final Pattern TEMPLATE_PARAM_PATTERN = Pattern.compile("\\$\\{(.+?)(:[a-zA-Z]+)?}");

    private static final Map<String, UnaryOperator<String>> FUNCTIONS = Map.of(
            "upperCase", String::toUpperCase,
            "lowerCase", String::toLowerCase,
            "capitalize", StringUtils::capitalize
    );

    private TemplateUtils() {}

    public static String processTemplate(String template, Map<String, String> context) {
        return TEMPLATE_PARAM_PATTERN.matcher(template).replaceAll(matchResult -> {
            String key = matchResult.group(1);
            if (!context.containsKey(key)) {
                return "\\" + matchResult.group();
            }
            String value = nullToEmpty(context.get(key));
            String function = removeStart(matchResult.group(2), ":");
            if (function != null) {
                if (FUNCTIONS.containsKey(function)) {
                    value = FUNCTIONS.get(function).apply(value);
                }
            }
            return Matcher.quoteReplacement(value);
        });
    }

}
```

ThrowingBiFunction

```java
@FunctionalInterface
public interface ThrowingBiFunction<T, U, R> {

    R apply(T t, U u) throws Exception;

}

public interface ThrowingRunnable {
    void run() throws ThingsboardException;

    default ThrowingRunnable andThen(ThrowingRunnable after) {
        return () -> {
            this.run();
            after.run();
        };
    }

}

@FunctionalInterface
public interface ThrowingSupplier<T> {

    T get() throws ThingsboardException;

}
```

GeoUtil

```java
GeoUtil.distance(entityCoordinates, perimeterCoordinates, rangeUnit)
```

ListeningExecutor

```java
public interface ListeningExecutor extends Executor {

    <T> ListenableFuture<T> executeAsync(Callable<T> task);

    default ListenableFuture<?> executeAsync(Runnable task) {
        return executeAsync(() -> {
            task.run();
            return null;
        });
    }

    default <T> ListenableFuture<T> submit(Callable<T> task) {
        return executeAsync(task);
    }

    default ListenableFuture<?> submit(Runnable task) {
        return executeAsync(task);
    }

}

public abstract class AbstractListeningExecutor implements ListeningExecutor {

    private ListeningExecutorService service;

    @PostConstruct
    public void init() {
        this.service = MoreExecutors.listeningDecorator(ThingsBoardExecutors.newWorkStealingPool(getThreadPollSize(), getClass()));
    }

    @PreDestroy
    public void destroy() {
        if (this.service != null) {
            this.service.shutdown();
        }
    }

    @Override
    public <T> ListenableFuture<T> executeAsync(Callable<T> task) {
        return service.submit(task);
    }

    public ListenableFuture<?> executeAsync(Runnable task) {
        return service.submit(task);
    }

    @Override
    public void execute(Runnable command) {
        service.execute(command);
    }

    public ListeningExecutorService executor() {
        return service;
    }

    protected abstract int getThreadPollSize();

}
```

DonAsynchron

```java
public class DonAsynchron {

    public static <T> void withCallback(ListenableFuture<T> future, Consumer<T> onSuccess,
                                        Consumer<Throwable> onFailure) {
        withCallback(future, onSuccess, onFailure, null);
    }

    public static <T> void withCallback(ListenableFuture<T> future, Consumer<T> onSuccess,
                                        Consumer<Throwable> onFailure, Executor executor) {
        FutureCallback<T> callback = new FutureCallback<T>() {
            @Override
            public void onSuccess(T result) {
                if (onSuccess == null) {
                    return;
                }
                try {
                    onSuccess.accept(result);
                } catch (Throwable th) {
                    onFailure(th);
                }
            }

            @Override
            public void onFailure(Throwable t) {
                if (onFailure == null) {
                    return;
                }
                onFailure.accept(t);
            }
        };
        if (executor != null) {
            Futures.addCallback(future, callback, executor);
        } else {
            Futures.addCallback(future, callback, MoreExecutors.directExecutor());
        }
    }

    public static <T> ListenableFuture<T> submit(Callable<T> task, Consumer<T> onSuccess, Consumer<Throwable> onFailure, Executor executor) {
        return submit(task, onSuccess, onFailure, executor, null);
    }

    public static <T> ListenableFuture<T> submit(Callable<T> task, Consumer<T> onSuccess, Consumer<Throwable> onFailure, Executor executor, Executor callbackExecutor) {
        ListenableFuture<T> future = Futures.submit(task, executor);
        withCallback(future, onSuccess, onFailure, callbackExecutor);
        return future;
    }

}
```

ExpressionFunctionsUtil

```java
userDefinedFunctions.add(Functions.getBuiltinFunction("sin"));
```

JacksonUtil

LinkedHashMapRemoveEldest

SslUtil

SystemUtil

RegexUtils

```
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class RegexUtils {

    public static final Pattern UUID_PATTERN = Pattern.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");

    private static final ConcurrentMap<String, Pattern> patternsCache = new ConcurrentReferenceHashMap<>(16, SOFT);

    public static String replace(String s, Pattern pattern, UnaryOperator<String> replacer) {
        return pattern.matcher(s).replaceAll(matchResult -> {
            return replacer.apply(matchResult.group());
        });
    }

    public static String replace(String input, @Language("regexp") String pattern, Function<MatchResult, String> replacer) {
        return patternsCache.computeIfAbsent(pattern, Pattern::compile).matcher(input).replaceAll(replacer);
    }

    public static boolean matches(String input, Pattern pattern) {
        return pattern.matcher(input).matches();
    }

    public static String getMatch(String input, Pattern pattern, int group) {
        Matcher matcher = pattern.matcher(input);
        if (matcher.find()) {
            try {
                return matcher.group(group);
            } catch (Exception ignored) {}
        }
        return null;
    }

}
```

TbBytePool

```java
public class TbBytePool {

    @Getter
    private static final ConcurrentMap<String, byte[]> pool = new ConcurrentReferenceHashMap<>();

    public static byte[] intern(byte[] data) {
        if (data == null) {
            return null;
        }
        var checksum = Hashing.sha512().hashBytes(data).toString();
        return pool.computeIfAbsent(checksum, c -> data);
    }

}
```

ThingsBoardExecutors

ThingsBoardForkJoinWorkerThreadFactory

ThingsBoardScheduledThreadPoolExecutor

ThingsBoardThreadFactory

四层架构：controller  -> service  -> dao/validator  -> repository

领域模型：

- HasEmail
- HasName
- HasTenantId
- HasAdditionalInfo
- HasVersion
- BaseData
- BaseDataWithAdditionalInfo
- ContactBased
- UUIDBased

后续准备继续补充这些模块的源码笔记：

- actor
- queue
- oauth2
- mqtt
- notice
- sms
- email
- proto
- websocket
- cache

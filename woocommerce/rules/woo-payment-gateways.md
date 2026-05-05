---
title: WooCommerce Payment Gateway Development
impact: CRITICAL
impactDescription: Payment errors cause lost revenue and compliance issues
tags: woocommerce, payment, gateway, webhook, refund
---

## WooCommerce Payment Gateway Development

**Impact: CRITICAL (payment handling is the most security-sensitive WooCommerce domain)**

Extend `WC_Payment_Gateway`. Implement `process_payment()` for checkout flow. Handle webhooks for async payment confirmation. Support refunds via `process_refund()`. Always validate webhook signatures.

## Bad Example

```php
class My_Gateway extends \WC_Payment_Gateway {
    public function process_payment( $order_id ) {
        $order = wc_get_order( $order_id );
        wp_remote_post( 'https://api.payment.com/charge', [
            'body' => [
                'amount'   => $order->get_total(),
                'card'     => $_POST['card_number'],
                'currency' => 'USD',
            ],
        ] );
        $order->update_status( 'completed' );
        return [ 'result' => 'success' ];
    }
}
```

## Good Example

```php
class My_Gateway extends \WC_Payment_Gateway {
    public function process_payment( $order_id ): array {
        $order = wc_get_order( $order_id );
        if ( ! $order ) {
            throw new \Exception( 'Invalid order' );
        }

        $response = wp_remote_post( 'https://api.payment.com/charge', [
            'body'    => wp_json_encode( [
                'amount'      => (float) $order->get_total(),
                'currency'    => $order->get_currency(),
                'order_id'    => $order->get_id(),
                'return_url'  => $this->get_return_url( $order ),
                'webhook_url' => home_url( '/wc-api/my_gateway_webhook' ),
            ] ),
            'headers' => [
                'Authorization' => 'Bearer ' . $this->api_key,
                'Content-Type'  => 'application/json',
            ],
            'timeout' => 30,
        ] );

        if ( is_wp_error( $response ) ) {
            throw new \Exception( $response->get_error_message() );
        }

        $body = json_decode( wp_remote_retrieve_body( $response ), true );
        if ( ! isset( $body['payment_url'] ) ) {
            throw new \Exception( 'Payment initiation failed' );
        }

        $order->update_meta_data( '_transaction_id', $body['payment_id'] );
        $order->save();

        return [
            'result'   => 'success',
            'redirect' => $body['payment_url'],
        ];
    }

    public function process_refund( $order_id, $amount = null, $reason = '' ): bool {
        $order = wc_get_order( $order_id );
        if ( ! $order ) {
            return false;
        }

        $transaction_id = $order->get_transaction_id();
        $response = wp_remote_post( 'https://api.payment.com/refund', [
            'body' => wp_json_encode( [
                'payment_id'     => $transaction_id,
                'amount'         => (float) $amount,
                'reason'         => $reason,
            ] ),
            'headers' => [ 'Authorization' => 'Bearer ' . $this->api_key ],
        ] );

        return ! is_wp_error( $response ) && 200 === wp_remote_retrieve_response_code( $response );
    }
}

// Webhook handler
add_action( 'woocommerce_api_my_gateway_webhook', function() {
    $payload = file_get_contents( 'php://input' );
    $signature = $_SERVER['HTTP_X_SIGNATURE'] ?? '';

    if ( ! my_verify_webhook_signature( $payload, $signature ) ) {
        status_header( 401 );
        exit;
    }

    $event = json_decode( $payload, true );
    $order = wc_get_order( $event['order_id'] );
    if ( $order && 'payment.completed' === $event['type'] ) {
        $order->payment_complete( $event['payment_id'] );
    }
    status_header( 200 );
    exit;
} );
```

## Why

- **Extend `WC_Payment_Gateway`** — integrates with WooCommerce checkout, settings, and admin
- **`process_payment()`** — must return `['result' => 'success', 'redirect' => $url]` or throw exception
- **Never handle card data directly** — redirect to payment provider or use tokenization
- **`$this->get_return_url($order)`** — proper WooCommerce return URL with order hash
- **Webhook verification** — always validate signature before processing
- **`$order->payment_complete()`** — triggers all payment completion hooks
- **`process_refund()`** — enables refund support from WooCommerce admin
- **Store transaction ID** — `$order->update_meta_data('_transaction_id', $id)` for reconciliation

Reference: [WC_Payment_Gateway](https://woocommerce.github.io/code-reference/classes/WC-Payment-Gateway.html) | [Payment Gateway API](https://developer.woocommerce.com/docs/payment-gateway-api/)

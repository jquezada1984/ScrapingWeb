#!/usr/bin/env python3
import pika
import json

def check_queue():
    try:
        # Conectar a RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('host.docker.internal', 5672))
        channel = connection.channel()
        
        # Verificar estado de la cola
        queue_info = channel.queue_declare(queue='aseguradora_queue', passive=True)
        print(f'📊 Estado de la cola:')
        print(f'   • Mensajes en cola: {queue_info.method.message_count}')
        print(f'   • Consumidores activos: {queue_info.method.consumer_count}')
        
        # Si hay mensajes, mostrar el primero
        if queue_info.method.message_count > 0:
            method, properties, body = channel.basic_get(queue='aseguradora_queue')
            if method:
                mensaje = json.loads(body.decode('utf-8'))
                print(f'📨 Primer mensaje en cola:')
                print(f'   • Tipo: {type(mensaje)}')
                claves = list(mensaje.keys()) if isinstance(mensaje, dict) else 'No es dict'
                print(f'   • Claves: {claves}')
                if 'Clientes' in mensaje:
                    total_clientes = len(mensaje['Clientes'])
                    print(f'   • Total clientes: {total_clientes}')
                    if mensaje['Clientes']:
                        primer_cliente = mensaje['Clientes'][0]
                        nombre = primer_cliente.get('NombreCompleto', 'Sin nombre')
                        print(f'   • Primer cliente: {nombre}')
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                print('❌ No se pudo obtener mensaje de la cola')
        else:
            print('📭 No hay mensajes en la cola')
        
        connection.close()
        return queue_info.method.message_count > 0
        
    except Exception as e:
        print(f'❌ Error verificando cola: {e}')
        return False

if __name__ == "__main__":
    check_queue()

import os
import django
from django.db import connection

from nieszkolni_app.models import Product
from nieszkolni_app.models import Order

from nieszkolni_folder.time_machine import TimeMachine
from nieszkolni_folder.cleaner import Cleaner

import re

from nieszkolni_folder.stream_manager import StreamManager
from nieszkolni_folder.curriculum_planner import CurriculumPlanner

os.environ["DJANGO_SETTINGS_MODULE"] = 'nieszkolni_folder.settings'
django.setup()


class ProductManager:
    def __init__(self):
        pass

    def add_product(
            self,
            title,
            description,
            category,
            points,
            quantity,
            allocation_per_client,
            status,
            image,
            reference
            ):

        now_number = TimeMachine().now_number()

        product = Product()
        product.creation_stamp = now_number
        product.modification_stamp = now_number
        product.title = Cleaner().clean_quotation_marks(title)
        product.description = Cleaner().clean_quotation_marks(description)
        product.category = category
        product.points = points
        product.quantity = quantity
        product.allocation_per_client = allocation_per_client
        product.status = status
        product.image = image
        product.reference = reference
        product.save()

    def update_product(
            self,
            title,
            description,
            category,
            points,
            quantity,
            allocation_per_client,
            status,
            image,
            reference,
            product_id
            ):

        now_number = TimeMachine().now_number()

        product = Product.objects.get(pk=product_id)
        product.modification_stamp = now_number
        product.title = Cleaner().clean_quotation_marks(title)
        product.description = Cleaner().clean_quotation_marks(description)
        product.category = category
        product.points = points
        product.quantity = quantity
        product.allocation_per_client = allocation_per_client
        product.status = status
        product.image = image
        product.reference = reference
        product.save()

    def run_order(
            self,
            product_id,
            client
            ):

        order_id = self.place_order(product_id, client)

        if order_id is not None:
            output = self.execute_order(order_id)
        else:
            output = ("ERROR", "Your order couldn't be realized")

        return output

    def place_order(
            self,
            product_id,
            client
            ):

        # try:
        now_number = TimeMachine().now_number()

        order = Order()
        order.creation_stamp = now_number
        order.modification_stamp = now_number
        order.product_id = product_id
        order.seller = ""
        order.client = client
        order.status = "placed"
        order.save()

        return order.pk

        # except Exception as e:
        #     print(e)
        #     return None

    def execute_order(
            self,
            order_id
            ):

        order = Order.objects.get(pk=order_id)
        product = Product.objects.get(pk=order.product_id)

        executed_orders = len(Order.objects.filter(
                client=order.client,
                product_id=order.product_id,
                status="executed"
                ))

        check_allocation = executed_orders < product.allocation_per_client

        if not check_allocation:
            output = ("ERROR", "This product is not available for you")
            return output

        if product.category == "course":
            course_ids_list = []
            course_ids_list.append(product.reference)

            CurriculumPlanner().plan_courses_now(
                order.client,
                order.client,
                course_ids_list
                )

            order.status = "executed"
            order.save()

            product.quantity = product.quantity - 1
            product.save()

            StreamManager().add_to_stream(
                order.client,
                "Activity",
                f"product {product.id};{product.points}",
                "automatic"
                )

            output = ("SUCCESS", ("You've signed up for the course"))
            return output
